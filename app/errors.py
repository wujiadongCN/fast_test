from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BizError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


def init_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BizError)
    async def handle_biz_error(request: Request, exc: BizError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": exc.code,
                "message": exc.msg,
                "errors": None,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_422(request: Request, exc: RequestValidationError):
        # 统一 422 返回体结构（见测试断言格式）
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 10001,
                "message": "validation error",
                "errors": exc.errors(),
                "path": request.url.path,
            },
        )
