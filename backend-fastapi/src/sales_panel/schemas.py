from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CategorySchema(BaseModel):
    title: str
    slug: str


class CategoryOut(CategorySchema):
    id: int


class ProductSchema(BaseModel):
    category_id: int
    slug: str
    mpn: str
    title: str
    brand: str
    description: str
    specifications: str
    price: Optional[float] = Field(None, ge=0, description="Цена товара")
    discount: Optional[int] = Field(
        None, ge=0, le=100, description="Скидка в процентах"
    )
    stock_quantity: int
    weight_kg: float
    average_mark: float


class ProductOut(ProductSchema):
    id: int


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    slug: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    weight_kg: Optional[float] = None
    average_mark: Optional[float] = None


class ProductPriceOrDiscountUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0, description="Цена товара")
    discount: Optional[int] = Field(
        None, ge=0, le=100, description="Скидка в процентах"
    )


class ProductStockQuantityUpdate(BaseModel):
    operation: str
    count: int
