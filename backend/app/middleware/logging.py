import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import set_request_id

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        set_request_id(request_id)

        start_time = time.perf_counter()

        logger.info(
            "%s %s",
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Response %d | %.2f ms",
            response.status_code,
            process_time,
        )

        return response