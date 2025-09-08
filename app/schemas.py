from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, examples=["Apple"])  # OpenAPI 示例
    price: float = Field(gt=0)
    description: Optional[str] = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    description: Optional[str] = None
    owner: str