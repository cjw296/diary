import random
import string

from httpx import Response
from testfixtures import compare

from fastapi.testclient import TestClient


# from app.core.config import settings


def check_response(response: Response, json: dict, status_code: int = 200) -> None:
    compare(response.status_code, expected=status_code, suffix=response.text)
    compare(response.json(), expected=json)


SUPERUSER_USERNAME = 'testsuperuser@example.com'
SUPERUSER_PASSWORD = '<PASSWORD>'


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    login_data = {"username": username, "password": password}
    r = client.post(f"/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200, r.text
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
