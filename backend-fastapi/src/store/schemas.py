from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.utils.enum import PaymentStatusEnum, DeliveryStatusEnum


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class ProductIdTitleMark(BaseModel):
    id: int
    title: str
    average_mark: float


class ProductIdTitleMarkBrand(ProductIdTitleMark):
    brand: str
    added_at: Optional[datetime] = None


class ProductIdTitleBrandPriceDiscount(BaseModel):
    id: int
    title: str
    brand: str
    price: float
    discount: int


class ProductsByBrand(BaseModel):
    brand: str
    products: list[ProductIdTitleMark]


class ProductSortedByBrandInCategory(BaseModel):
    category_id: int
    category_title: str
    category_slug: str
    brands: list[ProductsByBrand]


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class ReviewSchema(BaseModel):
    product_id: int
    comment: str
    mark: int


class ReviewOut(ReviewSchema):
    id: int
    user_id: int


class ReviewUpdate(BaseModel):
    comment: Optional[str] = None
    mark: Optional[int] = None


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class CartIn(BaseModel):
    product_id: int


class CartSchema(CartIn):
    user_id: int
    added_at: datetime


class CartOut(CartSchema):
    id: int


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class LikedIn(BaseModel):
    product_id: int


class LikedSchema(LikedIn):
    user_id: int
    added_at: datetime


class LikedOut(LikedSchema):
    id: int


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class PromoCodeSchema(BaseModel):
    id: int
    title: str
    code: str
    discount: int


class OrderProductsSchema(BaseModel):
    product_id: int


class OrderSchema(BaseModel):
    promo_code: Optional[str] = None
    delivery_address: str
    delivery_index: str
    products: list[OrderProductsSchema]


class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    total_price_without_discount: float
    payment_status: PaymentStatusEnum
    delivery_status: DeliveryStatusEnum
    delivery_address: str
    delivery_index: str
    promo_code_data: Optional[PromoCodeSchema] = None
    products: list[ProductIdTitleBrandPriceDiscount]
    payment_url: str
