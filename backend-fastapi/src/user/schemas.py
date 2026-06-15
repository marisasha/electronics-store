from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.utils.enum import GenderEnum, RoleEnum


class UserSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    gender: GenderEnum
    birth_date: datetime
    phone: str
    role: RoleEnum = RoleEnum.USER
    is_email_verificated: bool = False

    model_config = {"from_attributes": True}


class UserSchemaOut(UserSchema):
    id: int


class UserSchemaIn(UserSchema):
    password: str


class UserChangeDataSchema(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    phone: Optional[str] = None


class UserProfileSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class VerificationShema(BaseModel):
    user_id: int
    expires_at: datetime
    is_used: bool
    token: str


class VerificationIDShema(VerificationShema):
    id: int
