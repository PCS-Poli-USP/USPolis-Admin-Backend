from fastapi import status
from fastapi.testclient import TestClient

URL_PREFIX = "/static"


def test_get_existing_static_file(public_client: TestClient) -> None:
    response = public_client.get(f"{URL_PREFIX}/assets/uspolis-logo-email.png")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "image/png"


def test_get_missing_static_file(public_client: TestClient) -> None:
    response = public_client.get(f"{URL_PREFIX}/assets/does-not-exist.png")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_static_file_blocks_path_traversal(public_client: TestClient) -> None:
    # %2e%2e survives httpx's client-side URL normalization (a literal "../"
    # would be collapsed before the request is even sent), so this actually
    # reaches serve_static_file's is_relative_to(STATIC_DIR) guard.
    response = public_client.get(f"{URL_PREFIX}/%2e%2e/%2e%2e/pyproject.toml")
    assert response.status_code == status.HTTP_404_NOT_FOUND
