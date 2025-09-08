from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, examples=["Apple"])  # OpenAPI 示例
    price: float = Field(gt=0)
    description: str | None = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    description: str | None = None
    owner: str
