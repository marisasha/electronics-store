from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
class ProductIdTitleMark(BaseModel):
    id: int
    title: str
    average_mark: float


class ProductIdTitleMarkBrand(ProductIdTitleMark):
    brand: str
    added_at: Optional[datetime] = None


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
