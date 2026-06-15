from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.utils.enum import OrderStatusEnum

from datetime import datetime


class CategoryModel(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)


class ProductModel(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE")
    )
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    mpn: Mapped[str] = mapped_column(unique=True, nullable=False)
    title: Mapped[str]
    brand: Mapped[str]
    description: Mapped[str]
    specifications: Mapped[str]
    price: Mapped[float]
    discount: Mapped[int]
    stock_quantity: Mapped[int]
    weight_kg: Mapped[float]
    average_mark: Mapped[float]


class ProductImageModel(Base):
    __tablename__ = "product_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int]
    image_url: Mapped[str]
