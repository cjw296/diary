from testfixtures import compare

from fastapi.testclient import TestClient


def test_slash(client: TestClient):
    response = client.get("/")
    compare(response.status_code, expected=404)
    compare(response.json(), expected={'detail': 'Not Found'})
