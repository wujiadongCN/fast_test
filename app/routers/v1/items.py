from typing import Annotated

from celery.result import AsyncResult
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.celery_app import celery

from ...deps import PageParams, User, get_current_user, page_params
from ...schemas import ItemCreate, ItemOut
from ...services import audit_created, create_item, delete_item, get_item, list_items
from .meta import MailIn, TaskOut, TaskStatusOut
from .tasks import send_email_task

router = APIRouter()


@router.get("/health")
async def health():
    # 与 v1 区分一下返回内容
    return {"status": "ok"}


@router.post("/items", response_model=ItemOut)
async def create_item_ep(
    payload: ItemCreate,
    bg: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
):
    item = create_item(owner=user.name, data=payload)
    # 使用 BackgroundTasks 调用 audit_created(user.name, item.id)
    bg.add_task(audit_created, user.name, item.id)
    return item


@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item_ep(item_id: int, user: Annotated[User, Depends(get_current_user)]):
    it = get_item(item_id)
    if not it:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return it


@router.delete("/items/{item_id}")
async def delete_item_ep(item_id: int, user: Annotated[User, Depends(get_current_user)]):
    ok = delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"deleted": True}


@router.get("/items", response_model=list[ItemOut])
async def list_items_ep(
    pp: Annotated[PageParams, Depends(page_params)],
    user: Annotated[User, Depends(get_current_user)],
):
    # 返回分页列表（调用 services.list_items）
    return list_items(limit=pp.limit, offset=pp.offset)


@router.post("/send-email", response_model=TaskOut)
def enqueue_mail(payload: MailIn):
    """
    入队发送邮件任务，立即返回 task_id。
    """
    # 可在这里做幂等：例如从 Header 读取 Idempotency-Key 做去重
    async_result = send_email_task.delay(payload.to, payload.subject, payload.body)
    return TaskOut(task_id=async_result.id)


@router.get("/tasks/{task_id}", response_model=TaskStatusOut)
def get_task_status(task_id: str):
    """
    查询任务状态：PENDING / STARTED / RETRY / SUCCESS / FAILURE
    """
    res: AsyncResult = celery.AsyncResult(task_id)
    # 失败时 result 里通常是异常信息；成功时是任务返回值
    result = res.result if res.successful() else (res.result if res.failed() else None)
    return TaskStatusOut(
        task_id=task_id, state=res.state, result=result if isinstance(result, dict) else None
    )
