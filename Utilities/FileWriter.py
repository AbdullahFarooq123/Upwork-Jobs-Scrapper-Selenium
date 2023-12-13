import json


def write_seen_data(prev_data: list, filename: str = 'prev.json'):
    __write_data(prev_data, filename)


def __write_data(data, path: str):
    try:
        with open(path, 'w') as data_file:
            data_file.writelines(json.dumps(data, indent=4))
    except FileNotFoundError:
        return
