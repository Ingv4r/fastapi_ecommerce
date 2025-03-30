from __future__ import annotations

from pydantic import BaseModel


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
    rating: int
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
