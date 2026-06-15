from datetime import timedelta
import json
import random

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status
from sqlalchemy import delete, exists, select

from src.sales_panel.models import CategoryModel
from src.sales_panel.schemas import CategoryOut
from src.exeptions import exception_handler
from src.store.schemas import *
from src.store.models import *
from src.store.dependencies import SessionDep

# from src.redis.decorators import cache
# from src.tasks.email_sender import send_email

router = APIRouter(tags=["api", "store"], prefix="/api")


@router.get(
    "v1/store/categories",
    summary="Просмотр всех категорий товаров",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def get_categories(session: SessionDep) -> list[CategoryOut]:
    categories_execute = await session.execute(select(CategoryModel))

    categories = categories_execute.scalars().all()
    if not categories:
        return []

    categories_out = [
        CategoryOut.model_validate(category, from_attributes=True)
        for category in categories
    ]
    return categories_out


@router.get(
    "v1/store/categories/{categorie_id}/products",
    summary="Просмотр всех категорий товаров",
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    categorie_id: int,
    brand: str = Query(..., description="product brand"),
):
    pass
