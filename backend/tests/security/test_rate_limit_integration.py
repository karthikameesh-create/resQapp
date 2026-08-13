from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def test_rate_limit_returns_429():
    limiter = Limiter(key_func=get_remote_address)

    test_app = FastAPI()

    test_app.state.limiter = limiter
    test_app.add_middleware(SlowAPIMiddleware)

    test_app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,
    )

    @test_app.get("/limited")
    @limiter.limit("2/minute")
    def limited_endpoint(request: Request):
        return {"status": "ok"}

    client = TestClient(test_app)

    response_1 = client.get("/limited")
    response_2 = client.get("/limited")
    response_3 = client.get("/limited")

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_3.status_code == 429