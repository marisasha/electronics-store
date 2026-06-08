from datetime import datetime
import time
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.utils.enum import RoleEnum, GenderEnum


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[GenderEnum] = mapped_column(
        CheckConstraint("gender IN ('M', 'F')", name="check_gender_valid"),
    )
    birth_date: Mapped[datetime]
    phone: Mapped[str] = mapped_column(unique=True)
    role: Mapped[RoleEnum] = mapped_column(
        CheckConstraint(
            "role IN ('superadmin','admin','salesclerk','user')",
            name="check_role_valid",
        ),
        default="user",
        nullable=False,
    )
    is_email_verificated: Mapped[bool] = mapped_column(default=False, nullable=False)


class VerificationModel(Base):
    __tablename__ = "verification"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    code: Mapped[str]
    expires_at: Mapped[datetime]
    is_used: Mapped[bool] = mapped_column(default=False)
