from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.utils.enum import PaymentStatusEnum, DeliveryStatusEnum, OrderStatusEnum

from datetime import datetime
from decimal import Decimal


class ReviewModel(Base):
    __tablename__ = "product_review"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE")
    )
    comment: Mapped[str]
    mark: Mapped[int]

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),
    )


class CartModel(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE")
    )
    added_at: Mapped[datetime]


class LikedModel(Base):
    __tablename__ = "liked"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE")
    )
    added_at: Mapped[datetime]


class PromoCodeModel(Base):
    __tablename__ = "promo_code"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    code: Mapped[str] = mapped_column(unique=True)
    discount: Mapped[int]


class OrderModel(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    promo_code_id: Mapped[int | None] = mapped_column(
        ForeignKey("promo_code.id", ondelete="CASCADE")
    )
    payment_id: Mapped[str | None]
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        CheckConstraint(
            "payment_status IN ('PENDING','PAID','FAILED',CANCELLED)",
            name="check_payment_status_valid",
        ),
        index=True,
    )
    delivery_status: Mapped[DeliveryStatusEnum] = mapped_column(
        CheckConstraint(
            "delivery_status IN ('PROCESSING','SHIPPED','DELIVERED',COMPLETED)",
            name="check_delivery_status_valid",
        ),
        index=True,
    )
    delivery_address: Mapped[str]
    delivery_index: Mapped[str]
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    total_price_without_discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())


class OrderProductModel(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE")
    )
    price: Mapped[float]
    discount: Mapped[int]
