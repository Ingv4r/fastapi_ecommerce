from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class GetProduct(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: int
    image_url: str
    stock: int
    rating: float
    is_active: bool
    category_id: int
    supplier_id: int | None


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class GetCategory(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    parent_id: int | None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class GetUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    is_admin: bool
    is_customer: bool
    is_supplier: bool


class UserStatusUpdate(BaseModel):
    is_admin: bool = False
    is_supplier: bool = False
    is_customer: bool = False


class ReviewBase(BaseModel):
    comment: Optional[str] = Field(None, max_length=500)
    grade: float = Field(None, ge=1, le=10)
    product_id: Optional[int] = None


class ReviewCreate(ReviewBase):
    user_id: int


class ReviewUpdate(BaseModel):
    comment: Optional[str] = Field(None, max_length=500)
    grade: Optional[float] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class ReviewRead(ReviewBase):
    id: int
    comment_date: datetime
    is_active: bool
    user_id: int

    class Config:
        from_attributes = True


class CeleryMessage(BaseModel):
    message: Optional[str] = None
