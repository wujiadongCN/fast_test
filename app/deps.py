from __future__ import annotations
from typing import Annotated, Optional
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, Field


# ---- 认证依赖 ----
class User(BaseModel):
    name: str


def _parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


async def get_current_user(authorization: Annotated[Optional[str], Header()]=None):
    """
    从 Authorization: Bearer <token> 中解析用户名，并返回 User。
    规则：token 直接等于用户名（练习用）。
    """
    token = _parse_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(name=token)


# ---- 分页依赖 ----
class PageParams(BaseModel):
    limit: int = Field(10, ge=1, le=100, description="每页数量")
    offset: int = Field(0, ge=0, description="偏移量")


async def page_params(
    limit: Annotated[int, Header()] = 10,  # 也支持 Query，练习用 Header 演示
    offset: Annotated[int, Header()] = 0,
) -> PageParams:
    return PageParams(limit=limit, offset=offset)


# ---- DB 会话占位（演示 DI 结构）----
class DBSess:
    def __init__(self):
        self.alive = True


async def get_db() -> DBSess:
    # 可在此放置生命周期管理逻辑（例如连接池获取/释放）
    return DBSess()