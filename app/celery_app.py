# app/celery_app.py
from celery import Celery

from app.settings import settings  # 使用相对导入，避免同名模块冲突

celery = Celery(
    "mail_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.set_default()

# 非 Django 项目需要明确告诉它去哪些包里找 tasks.py
celery.autodiscover_tasks(["app.routers.v1"])

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_time_limit=30,  # 硬超时
    task_soft_time_limit=25,  # 软超时（Windows 下会忽略软超时提示）
)
