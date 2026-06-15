from fastapi import APIRouter

from src.auth.service import router as auth_router
from src.user.service import router as user_router
from src.sales_panel.service import router as sales_panel_router
from src.store.service import router as store_router

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(sales_panel_router)
main_router.include_router(store_router)
