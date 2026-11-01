"""Exercise the actual UI against a disposable data folder."""
from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

import settings
import storage
from json_store import StorageError

ROOT = Path(__file__).resolve().parents[1]


def item(elements, label):
    return next(element for element in elements if element.label == label)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'DATA_FILE', tmp_path / 'checkins.json')
    monkeypatch.setattr(settings, 'SETTINGS_FILE', tmp_path / 'settings.json')
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
    assert not at.exception
    return at


def test_checkin_and_settings_save_from_their_forms(app):
    item(app.button, 'save check-in').click().run()
    assert not app.exception
    assert len(storage.load_checkins()) == 1
    item(app.text_input, 'name').input('Example').run()
    item(app.selectbox, 'preferred tone').select('direct').run()
    item(app.button, 'save settings').click().run()
    assert not app.exception
    assert settings.load_settings()['name'] == 'Example'
    assert settings.load_settings()['preferred_tone'] == 'direct'


def test_failed_save_does_not_change_session_history(app):
    with patch('renderers.append_checkin', side_effect=StorageError('Could not save checkins.json.')):
        item(app.button, 'save check-in').click().run()
    assert not app.exception
    assert app.session_state['checkins'] == []
    assert not storage.DATA_FILE.exists()
    assert any('Could not save' in error.value for error in app.error)
    assert not any('check-in saved' in message.value for message in app.success)


def test_corrupt_file_blocks_app_with_recovery_message(tmp_path, monkeypatch):
    path = tmp_path / 'checkins.json'
    path.write_text('{broken')
    monkeypatch.setattr(storage, 'DATA_FILE', path)
    monkeypatch.setattr(settings, 'SETTINGS_FILE', tmp_path / 'settings.json')
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
    assert not app.exception
    assert any('preserved' in error.value for error in app.error)
    assert not app.button
    assert path.read_text() == '{broken'
