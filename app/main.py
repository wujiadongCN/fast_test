from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

from .middlewares import add_middlewares
from .errors import init_error_handlers
from .routers.v1.meta import router as meta_v1
from .routers.v1.items import router as items_v1
from .routers.v2.meta import router as meta_v2

from celery.result import AsyncResult
from app.celery_app import celery
from app.routers.v1.tasks import add, send_email_task


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Practice", version="1.0.0")
    print("broker_url =>", celery.conf.broker_url)
    print("result_backend =>", celery.conf.result_backend)
    print("task app broker =>", add.app.conf.broker_url)
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

    class MailIn(BaseModel):
        to: EmailStr
        subject: str = Field(min_length=1, max_length=200)
        body: str = Field(min_length=1, max_length=5000)

    class TaskOut(BaseModel):
        task_id: str

    class TaskStatusOut(BaseModel):
        task_id: str
        state: str
        result: dict | None = None

    @app.post("/send-email", response_model=TaskOut)
    def enqueue_mail(payload: MailIn):
        """
        入队发送邮件任务，立即返回 task_id。
        """
        # 可在这里做幂等：例如从 Header 读取 Idempotency-Key 做去重
        print(payload.model_dump())
        async_result = add.delay(1, 2)
        # async_result = celery.send_task("app.routers.v1.tasks.add", args=[1, 2])
        # async_result = send_email_task.delay(payload.to, payload.subject, payload.body)
        return TaskOut(task_id=async_result.id)

    @app.get("/tasks/{task_id}", response_model=TaskStatusOut)
    def get_task_status(task_id: str):
        """
        查询任务状态：PENDING / STARTED / RETRY / SUCCESS / FAILURE
        """
        res: AsyncResult = celery.AsyncResult(task_id)
        # 失败时 result 里通常是异常信息；成功时是任务返回值
        result = res.result if res.successful() else (res.result if res.failed() else None)
        return TaskStatusOut(task_id=task_id, state=res.state, result=result if isinstance(result, dict) else None)

    return app


app = create_app()
