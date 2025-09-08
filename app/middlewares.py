import time
import uuid

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", str(uuid.uuid4()))
        return response


class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            cost_ms = (time.perf_counter() - start) * 1000
            # 只在成功获取响应时才添加header
            if response is not None and "x-process-time" not in response.headers:
                response.headers["X-Process-Time"] = f"{cost_ms:.2f}ms"


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimerMiddleware)
