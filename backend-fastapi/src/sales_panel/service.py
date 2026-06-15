from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status
from sqlalchemy import delete, exists, select


from src.exeptions import exception_handler
from src.sales_panel.schemas import *
from src.sales_panel.models import *
from src.sales_panel.dependencies import SessionDep

# from src.redis.decorators import cache
# from src.tasks.email_sender import send_email

router = APIRouter(tags=["api", "sales panel"], prefix="/api")


@router.post(
    "/v1/sales-panel/categories",
    summary="Создание новой категории товаров",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def create_category(
    category_in: CategorySchema, session: SessionDep
) -> CategoryOut:
    category_dict = category_in.model_dump()
    for field in ["title", "slug"]:
        is_field_exists = await session.execute(
            select(
                exists().where(getattr(CategoryModel, field) == category_dict[field])
            )
        )
        if is_field_exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.title()} already exists",
            )

    new_category = CategoryModel(title=category_in.title.title(), slug=category_in.slug)

    session.add(new_category)
    await session.commit()

    category_out = CategoryOut.model_validate(new_category, from_attributes=True)
    return category_out


@router.put(
    "/v1/sales-panel/categories/{category_id}",
    summary="Обновление данных категории по category_id",
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int, category_in: CategorySchema, session: SessionDep
) -> CategoryOut:
    category = await session.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    update_data = category_in.model_dump(exclude_unset=True)
    for field in ["title", "slug"]:
        if field in update_data:
            is_field_exists = await session.execute(
                select(
                    exists().where(getattr(CategoryModel, field) == update_data[field])
                )
            )
            if is_field_exists.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field.title()} already exists",
                )

    for field, value in update_data.items():
        setattr(category, field, value)

    await session.commit()
    return category


@router.delete(
    "/v1/sales-panel/categories/{category_id}",
    summary="Удаление категории по category_id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(category_id: int, session: SessionDep) -> None:
    category_execute = await session.execute(
        delete(CategoryModel).where(CategoryModel.id == category_id)
    )

    if category_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    await session.commit()


@router.post(
    "/v1/sales-panel/products",
    summary="Создание нового товара",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def create_product(product_in: ProductSchema, session: SessionDep) -> ProductOut:
    product_dict = product_in.model_dump()
    for field in ["mpn", "slug"]:
        is_field_exists = await session.execute(
            select(exists().where(getattr(ProductModel, field) == product_dict[field]))
        )
        if is_field_exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.title()} already exists",
            )

    new_product = ProductModel(
        category_id=product_in.category_id,
        slug=product_in.slug,
        mpn=product_in.mpn,
        title=product_in.title,
        brand=product_in.brand,
        description=product_in.description,
        specifications=product_in.specifications,
        price=product_in.price,
        discount=product_in.discount,
        stock_quantity=product_in.stock_quantity,
        weight_kg=product_in.weight_kg,
        average_mark=product_in.average_mark,
    )

    session.add(new_product)
    await session.commit()

    product_out = ProductOut.model_validate(new_product, from_attributes=True)
    return product_out


@router.get(
    "/v1/sales-panel/products/{product_id}",
    summary="Просмотр конкретного товара по product_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def check_product(product_id: int, session: SessionDep) -> ProductOut:
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    product_out = ProductOut.model_validate(product, from_attributes=True)
    return product_out


@router.patch(
    "/v1/sales-panel/products/{product_id}",
    summary="Обновление информации о товаре по product_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def update_product(
    product_id: int, product_in: ProductInfoUpdate, session: SessionDep
) -> ProductOut:
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product} not found",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field in ["title", "slug"]:
        if field in update_data:
            is_field_exists = await session.execute(
                select(
                    exists().where(getattr(CategoryModel, field) == update_data[field])
                )
            )
            if is_field_exists.scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field.title()} already exists",
                )

    for field, value in update_data.items():
        setattr(product, field, value)

    await session.commit()
    return product


@router.patch(
    "/v1/sales-panel/products/{product_id}/price-discount",
    summary="Обновление цены или скидки о товаре по product_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def update_product_price(
    product_id: int, product_in: ProductPriceOrDiscountUpdate, session: SessionDep
) -> ProductOut:
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product} not found",
        )
    if product_in.price:
        product.price = product_in.price
    if product_in.discount:
        product.discount = product_in.discount

    await session.commit()
    return product


@router.patch(
    "/v1/sales-panel/products/{product_id}/stock-quantity",
    summary="Обновление количества товара по product_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def update_product_count(
    product_id: int, product_update_in: ProductStockQuantityUpdate, session: SessionDep
) -> ProductOut:
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product} not found",
        )
    if product_update_in.operation == "ADD":
        product.stock_quantity += product_update_in.count
    if product_update_in.operation == "REMOVE":
        product.stock_quantity -= product_update_in.count
    await session.commit()
    return product


@router.delete(
    "/v1/sales-panel/products/{product_id}",
    summary="Удаление товара по product_id",
    status_code=status.HTTP_204_NO_CONTENT,
)
@exception_handler
async def delete_product(product_id: int, session: SessionDep) -> None:
    product_execute = await session.execute(
        delete(CategoryModel).where(CategoryModel.id == product_id)
    )

    if product_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {product_id} not found",
        )

    await session.commit()
