from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict
from fastapi import HTTPException
from fastapi import status
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from dotenv import load_dotenv
from src.auth.schemas import CurrentUserSchema
from src.config import settings
import os

security = HTTPBearer(auto_error=True)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, str]) -> str:
    access_data = data.copy()
    access_expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt.access_token_expire_minutes
    )
    access_data.update({"exp": access_expire, "type": "access"})
    access_token = jwt.encode(access_data, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    return access_token


def create_refresh_token(data: Dict[str, str]) -> str:
    refresh_data = data.copy()
    refresh_expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt.refresh_token_expire_days
    )
    refresh_data.update({"exp": refresh_expire, "type": "refresh"})
    refresh_token = jwt.encode(refresh_data, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    return refresh_token


async def decode_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUserSchema:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected access token.",
            )

        id = payload.get("sub")
        if id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        role = payload.get("role")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        current_user = CurrentUserSchema(id=int(id), role=role)
        return current_user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def decode_refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected access token.",
            )

        id = payload.get("sub")
        if id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        role = payload.get("role")
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        current_user = CurrentUserSchema(id=int(id), role=role)
        return current_user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
