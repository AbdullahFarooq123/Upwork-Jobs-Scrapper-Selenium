import json


def read_category_feed_data(filename: str = 'data.json') -> dict:
    return __read_data(filename, {})


def read_prev_seen_jobs(filename: str = 'prev.json') -> list:
    return __read_data(filename, [])


def read_settings_data(filename: str = 'settings.json') -> dict:
    return __read_data(filename, {})


def __read_data(path: str, exception_return):
    try:
        with open(path, 'r') as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return exception_return
