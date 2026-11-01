from datetime import datetime
import math

from json_store import DATA_DIR, update_json, read_json

DATA_FILE = DATA_DIR / 'checkins.json'


def validate_checkins(value):
    if not isinstance(value, list):
        raise ValueError('check-ins must be a list')
    for row in value:
        if not isinstance(row, dict):
            raise ValueError('each check-in must be an object')
        for field, low, high in [('mood', 1, 10), ('stress', 1, 10), ('anxiety', 1, 10),
                                 ('sleep', 0, 12), ('energy', 1, 10)]:
            number = row.get(field)
            if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number) or not low <= number <= high:
                raise ValueError('invalid check-in score')
        if not isinstance(row.get('date'), str):
            raise ValueError('check-in date is required')
        datetime.fromisoformat(row['date'])
        if not isinstance(row.get('note', ''), str):
            raise ValueError('note must be text')
    return value


def load_checkins():
    return read_json(DATA_FILE, list, validate_checkins)


def save_checkins(checkins):
    return update_json(DATA_FILE, list, validate_checkins, lambda current: checkins)


def append_checkin(checkin):
    # Reload inside the process lock so another session's new entries survive.
    return update_json(DATA_FILE, list, validate_checkins, lambda current: current + [checkin])
