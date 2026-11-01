"""Durability and independent-session checks using temporary data only."""
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

import json_store
from json_store import StorageError
import settings
import storage

ROOT = Path(__file__).resolve().parents[1]
CHECKIN = {'date':'2026-10-31 09:00', 'mood':5, 'stress':5, 'anxiety':5, 'sleep':7, 'energy':5, 'note':'sample'}


@pytest.fixture
def data_path(tmp_path, monkeypatch):
    path = tmp_path / 'checkins.json'
    monkeypatch.setattr(storage, 'DATA_FILE', path)
    return path


def test_append_reads_latest_history_and_keeps_previous_version(data_path):
    storage.append_checkin(CHECKIN)
    storage.append_checkin({**CHECKIN, 'note':'second session'})
    assert len(storage.load_checkins()) == 2
    assert json.loads(Path(str(data_path) + '.bak').read_text()) == [CHECKIN]
    assert data_path.stat().st_mode & 0o777 == 0o600


def test_failed_replace_leaves_history_intact(data_path):
    storage.append_checkin(CHECKIN)
    original = data_path.read_bytes()
    replace = os.replace
    def fail_target(src, dest):
        if Path(dest) == data_path:
            raise OSError('simulated disk failure')
        return replace(src, dest)
    with patch.object(json_store.os, 'replace', side_effect=fail_target):
        with pytest.raises(StorageError):
            storage.append_checkin({**CHECKIN, 'note':'not saved'})
    assert data_path.read_bytes() == original
    assert not list(data_path.parent.glob('.checkins.json-*'))


@pytest.mark.parametrize('payload', ['{broken', '{}', '[{}]', 'null'])
def test_bad_existing_data_is_never_replaced(data_path, payload):
    data_path.write_text(payload)
    with pytest.raises(StorageError):
        storage.append_checkin(CHECKIN)
    assert data_path.read_text() == payload
    assert not Path(str(data_path) + '.bak').exists()


@pytest.mark.parametrize('change', [{'mood':float('nan')}, {'sleep':99}, {'energy':True}, {'date':'bad-date'}, {'note':[]}])
def test_invalid_new_entry_preserves_history(data_path, change):
    storage.append_checkin(CHECKIN)
    with pytest.raises(StorageError):
        storage.append_checkin({**CHECKIN, **change})
    assert storage.load_checkins() == [CHECKIN]


def test_concurrent_processes_do_not_lose_checkins(data_path):
    code = '''import json, sys
from pathlib import Path
import storage
storage.DATA_FILE = Path(sys.argv[1])
storage.append_checkin(json.loads(sys.argv[2]))
'''
    processes = [subprocess.Popen([sys.executable, '-B', '-c', code, str(data_path), json.dumps({**CHECKIN, 'note':str(i)})],
                                   cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in range(8)]
    for process in processes:
        out, err = process.communicate(timeout=20)
        assert process.returncode == 0, err.decode()
    assert {row['note'] for row in storage.load_checkins()} == {str(i) for i in range(8)}


def test_data_folder_override_is_independent_of_working_directory(tmp_path):
    folder = tmp_path / 'private-data'
    code = '''import json, storage
storage.append_checkin(json.loads(__import__('sys').argv[1]))
print(storage.DATA_FILE)
'''
    result = subprocess.run([sys.executable, '-B', '-c', code, json.dumps(CHECKIN)], cwd=tmp_path,
                            env=dict(os.environ, FRAME2MENTAL_DATA_DIR=str(folder), PYTHONPATH=str(ROOT)),
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert json.loads((folder / 'checkins.json').read_text()) == [CHECKIN]
    assert not (tmp_path / 'checkins.json').exists()


def test_invalid_settings_are_reported_without_overwriting(tmp_path, monkeypatch):
    path = tmp_path / 'settings.json'
    monkeypatch.setattr(settings, 'SETTINGS_FILE', path)
    settings.save_settings({'name':'Test'})
    before = path.read_bytes()
    with pytest.raises(StorageError):
        settings.save_settings({'preferred_tone':'unknown'})
    assert path.read_bytes() == before
