from datetime import time

from json_store import DATA_DIR, read_json, update_json

SETTINGS_FILE = DATA_DIR / 'settings.json'
DEFAULT_SETTINGS = {
    'name': '',
    'preferred_tone': 'calm',
    'focus_area': 'stress',
    'daily_reminder': '09:00',
}


def validate_settings(value):
    if not isinstance(value, dict):
        raise ValueError('settings must be an object')
    result = {**DEFAULT_SETTINGS, **value}
    if not all(isinstance(result[key], str) for key in DEFAULT_SETTINGS):
        raise ValueError('settings fields must be text')
    if result['preferred_tone'] not in ['calm', 'direct', 'encouraging']:
        raise ValueError('unknown tone')
    if result['focus_area'] not in ['stress', 'anxiety', 'sleep', 'burnout', 'self-awareness']:
        raise ValueError('unknown focus area')
    time.fromisoformat(result['daily_reminder'])
    return result


def load_settings():
    return read_json(SETTINGS_FILE, dict, validate_settings)


def save_settings(settings):
    return update_json(SETTINGS_FILE, dict, validate_settings, lambda current: {**current, **settings})
