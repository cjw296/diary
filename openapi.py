import api
import json


def generate():
    print(json.dumps(api.app.openapi()))


if __name__ == '__main__':
    # Pretty print with:
    # uv run openapi.py | jq .
    generate()
