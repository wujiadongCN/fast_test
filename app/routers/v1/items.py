from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from ...deps import get_current_user, page_params, PageParams
from ...schemas import ItemCreate, ItemOut
from ...services import create_item, get_item, delete_item, list_items, audit_created

router = APIRouter()


@router.post("/items", response_model=ItemOut)
async def create_item_ep(
    payload: ItemCreate,
    bg: BackgroundTasks,
    user=Depends(get_current_user),
):
    item = create_item(owner=user.name, data=payload)
    # 使用 BackgroundTasks 调用 audit_created(user.name, item.id)
    bg.add_task(audit_created, user.name, item.id)
    return item


@router.get("/items/{item_id}", response_model=ItemOut)
async def get_item_ep(item_id: int, user=Depends(get_current_user)):
    it = get_item(item_id)
    if not it:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return it


@router.delete("/items/{item_id}")
async def delete_item_ep(item_id: int, user=Depends(get_current_user)):
    ok = delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"deleted": True}


@router.get("/items", response_model=list[ItemOut])
async def list_items_ep(pp: PageParams = Depends(page_params), user=Depends(get_current_user)):
    # 返回分页列表（调用 services.list_items）
    return list_items(limit=pp.limit, offset=pp.offset)