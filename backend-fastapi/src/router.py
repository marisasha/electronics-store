from fastapi import APIRouter

from src.auth.service import router as auth_router
from src.user.service import router as user_router

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(user_router)

