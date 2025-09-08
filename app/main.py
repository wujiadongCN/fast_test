from fastapi import FastAPI

from app.celery_app import celery

from .errors import init_error_handlers
from .middlewares import add_middlewares
from .routers.v1.items import router as items_v1
from .routers.v1.meta import router as meta_v1
from .routers.v2.meta import router as meta_v2


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Practice", version="1.0.0")
    try:
        result = celery.control.ping()
        print("Celery connection test:", result)
    except Exception as e:
        print("Celery connection error:", e)

    # 中间件
    add_middlewares(app)

    # 异常处理
    init_error_handlers(app)

    # 路由 - v1
    app.include_router(meta_v1, prefix="/api/v1", tags=["meta"])
    app.include_router(items_v1, prefix="/api/v1", tags=["items"])

    # 路由 - v2（演示版本化）
    app.include_router(meta_v2, prefix="/api/v2", tags=["meta-v2"])

    @app.get("/health", status_code=200)
    def health():
        return {"status": "ok"}

    return app


app = create_app()
