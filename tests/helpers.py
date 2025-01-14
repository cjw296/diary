import random
import string
from itertools import chain
from typing import Iterable

from httpx import Response
from pydantic import BaseModel
from testfixtures import compare
from testfixtures.comparison import register, compare_object, CompareContext

from fastapi.testclient import TestClient


def compare_mapped_object(
    x, y, context: 'CompareContext', ignore_attributes: Iterable[str] = ()
) -> str | None:
    return compare_object(
        x,
        y,
        context=context,
        ignore_attributes=tuple(chain(ignore_attributes, ['_sa_instance_state', '__dict__'])),
    )


register(BaseModel, compare_mapped_object)


def check_response(response: Response, json: dict, status_code: int = 200) -> None:
    compare(response.status_code, expected=status_code, suffix=response.text)
    compare(response.json(), expected=json)


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


SUPERUSER_USERNAME = 'testsuperuser@example.com'
SUPERUSER_PASSWORD = random_lower_string()


NORMAL_USERNAME = 'testnormaluser@example.com'
NORMAL_PASSWORD = random_lower_string()


def get_user_token_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    login_data = {"username": username, "password": password}
    r = client.post(f"/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200, r.text
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
