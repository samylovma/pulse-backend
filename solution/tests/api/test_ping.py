from litestar.status_codes import HTTP_200_OK
from litestar.testing import create_test_client

from pulse_backend.api.ping import ping


def test_ping():
    with create_test_client(ping) as client:
        response = client.get("/api/ping")
        assert response.status_code == HTTP_200_OK
        assert response.text == "ok"
