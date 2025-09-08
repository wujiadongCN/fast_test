from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class LoginIn(BaseModel):
    username: str


class LoginOut(BaseModel):
    token: str


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


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn):
    # 练习：这里简单返回 Bearer 的 token（直接等于用户名）
    return {"token": payload.username}
