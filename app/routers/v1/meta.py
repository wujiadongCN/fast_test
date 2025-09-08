from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginIn(BaseModel):
    username: str


class LoginOut(BaseModel):
    token: str


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn):
    # 练习：这里简单返回 Bearer 的 token（直接等于用户名）
    return {"token": payload.username}
