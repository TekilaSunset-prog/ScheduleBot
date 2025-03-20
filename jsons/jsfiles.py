import json


def get_param(param='admins'):
    with open(f'jsons/cfg.json', 'r', encoding='UTF-8') as f:
        data = json.load(f).get(param.lower())

    return data
