from __future__ import annotations
from typing import Dict, List, Tuple
from .schemas import ItemOut, ItemCreate


# 简易内存 DB
DB: Dict[int, ItemOut] = {}
NEXT_ID: int = 1

# 审计日志（写入简单列表以便测试）
AUDIT_LOG: List[Tuple[str, int]] = []  # (username, item_id)


def clear_state():
    global DB, NEXT_ID, AUDIT_LOG
    DB.clear()
    NEXT_ID = 1
    AUDIT_LOG.clear()


def create_item(owner: str, data: ItemCreate) -> ItemOut:
    global NEXT_ID
    item = ItemOut(id=NEXT_ID, name=data.name, price=data.price, description=data.description, owner=owner)
    DB[NEXT_ID] = item
    NEXT_ID += 1
    return item


def get_item(item_id: int) -> ItemOut | None:
    return DB.get(item_id)


def delete_item(item_id: int) -> bool:
    return DB.pop(item_id, None) is not None


def list_items(limit: int, offset: int) -> list[ItemOut]:
    items = list(DB.values())
    # 按 offset/limit 做分页切片
    return items[offset:offset + limit]


def audit_created(owner: str, item_id: int) -> None:
    # 写入 AUDIT_LOG（见测试）
    AUDIT_LOG.append((owner, item_id))