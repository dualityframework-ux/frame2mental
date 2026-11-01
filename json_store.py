"""Atomic local JSON persistence for the macOS/Linux app."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import tempfile


class StorageError(RuntimeError):
    """A save or load failed; existing data must be recovered before continuing."""


DATA_DIR = Path(os.environ.get('FRAME2MENTAL_DATA_DIR', Path(__file__).resolve().parent)).expanduser().resolve()


def read_json(path, default, validate):
    path = Path(path)
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return validate(default())
    except (OSError, ValueError) as exc:
        raise StorageError(f'Could not read {path.name}. The file was preserved; recover it before continuing.') from exc
    try:
        return validate(value)
    except (ValueError, TypeError, KeyError) as exc:
        raise StorageError(f'{path.name} contains invalid data. The file was preserved; recover it before continuing.') from exc


@contextmanager
def _locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(str(path) + '.lock', os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, 'a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _replace(path, payload):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name + '-', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def update_json(path, default, validate, change):
    """Read latest data under a process lock, validate, back up, then replace."""
    path = Path(path)
    try:
        with _locked(path):
            current = read_json(path, default, validate)
            result = validate(change(current))
            payload = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
            if path.exists():
                _replace(Path(str(path) + '.bak'), path.read_text(encoding='utf-8'))
            _replace(path, payload)
            return result
    except StorageError:
        raise
    except (ValueError, TypeError, KeyError) as exc:
        raise StorageError(f'Invalid data for {path.name}. Check the form values; your previous data was preserved.') from exc
    except OSError as exc:
        raise StorageError(f'Could not save {path.name}. Your change was not saved; check the data folder and try again.') from exc
