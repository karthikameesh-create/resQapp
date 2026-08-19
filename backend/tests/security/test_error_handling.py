from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exception_handlers import generic_exception_handler


def test_generic_exception_does_not_leak_details():
    app = FastAPI()

    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )

    @app.get("/boom")
    def boom():
        raise RuntimeError(
            "SECRET_DATABASE_PASSWORD=super-secret "
            "/home/private/project traceback"
        )

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/boom")

    assert response.status_code == 500

    data = response.json()

    assert data == {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        },
    }

    body = response.text

    assert "SECRET_DATABASE_PASSWORD" not in body
    assert "super-secret" not in body
    assert "/home/private/project" not in body
    assert "RuntimeError" not in body