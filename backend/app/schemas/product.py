from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    created_by: str | None = Field(default=None, max_length=64)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: str
    created_at: datetime


class ProductList(BaseModel):
    items: list[ProductRead]
    total: int
