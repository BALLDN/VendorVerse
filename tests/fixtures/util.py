import json
import os


def load_fixtures():
    with open('tests/fixtures/data.json', 'r') as f:
        data = json.loads(f.read())
    return data


load_fixtures()
