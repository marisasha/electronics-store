from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status
from sqlalchemy import delete, exists, select

from src.auth.schemas import CurrentUserSchema
from src.auth.security import decode_access_token

from src.sales_panel.models import CategoryModel, ProductModel
from src.sales_panel.schemas import CategoryOut, ProductOut

from src.store.schemas import *
from src.store.models import *
from src.store.dependencies import SessionDep

from src.exeptions import exception_handler
from src.youkassa import create_payment

# from src.redis.decorators import cache
# from src.tasks.email_sender import send_email

router = APIRouter(tags=["api store"], prefix="/api/v1/store")


@router.get(
    "/categories",
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
    "/products/top",
    summary="Просмотр count самых популрных товаров в магазине",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def get_top_products(
    session: SessionDep,
    count: int = Query(..., ge=1, le=100, description="Количество выборки топа"),
) -> list[ProductIdTitleMark]:

    if count <= 0:
        raise HTTPException(
            detail="Количество выборки должно быть положительным",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    products_execute = await session.execute(
        select(ProductModel).order_by(ProductModel.average_mark.desc()).limit(count)
    )
    products = products_execute.scalars().all()
    if not products:
        return []

    products_out = [
        ProductIdTitleMarkBrand.model_validate(product, from_attributes=True)
        for product in products
    ]

    return products_out


@router.get(
    "/categories/{category_id}/products",
    summary="Просмотр 5 самых популрных товаров отсортированных по брендам в категории category_id",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def get_products_by_category(
    category_id: int, session: SessionDep
) -> ProductSortedByBrandInCategory:
    category = await session.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(
            detail=f"Category with id {category_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    products_execute = await session.execute(
        select(ProductModel)
        .where(ProductModel.category_id == category.id)
        .order_by(ProductModel.brand, ProductModel.average_mark.desc())
    )
    products = products_execute.scalars().all()
    if not products:
        return ProductSortedByBrandInCategory(
            category_id=category.id,
            category_title=category.title,
            category_slug=category.slug,
            brands=[],
        )

    brands_dict = {}
    for product in products:
        if product.brand not in brands_dict:
            brands_dict[product.brand] = []

        if len(brands_dict[product.brand]) < 5:
            brands_dict[product.brand]["products"].append(
                ProductIdTitleMark.model_validate(product, from_attributes=True)
            )

    brands_in_category = [
        ProductsByBrand(brand=brand, products=prods)
        for brand, prods in brands_dict.items()
    ]

    return ProductSortedByBrandInCategory(
        category_id=category.id,
        category_title=category.title,
        category_slug=category.slug,
        brands=brands_in_category,
    )


@router.get(
    "/products/by-brand/{brand}",
    summary="Просмотр товаров бренду ",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def get_products_by_brand(brand: str, session: SessionDep) -> ProductsByBrand:

    products_execute = await session.execute(
        select(ProductModel)
        .where(ProductModel.brand == brand)
        .order_by(ProductModel.average_mark.desc())
    )

    products = products_execute.scalars().all()
    if not products:
        return ProductsByBrand(brand=brand, products=[])

    products_out = ProductsByBrand(
        brand=brand,
        products=[
            ProductIdTitleMark.model_validate(product, from_attributes=True)
            for product in products
        ],
    )

    return products_out


@router.get(
    "/products/{product_id}",
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


@router.get(
    "/products/{product_id}/review",
    summary="Просмотр отзывов к товару от пользователей",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def get_reviews(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> list[ReviewOut]:
    reviews_execute = await session.execute(
        select(ReviewModel).where(ReviewModel.product_id == product_id)
    )
    reviews = reviews_execute.scalars().all()
    if not reviews:
        return []

    review_out = [
        ReviewOut.model_validate(review, from_attributes=True) for review in reviews
    ]

    return review_out


@router.post(
    "/rewiew",
    summary="Создание отзыва к товару от пользователя",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def create_review(
    review_in: ReviewSchema,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> ReviewOut:
    review_exist_execute = await session.execute(
        select(
            exists().where(
                ReviewModel.user_id == current_user.id,
                ReviewModel.product_id == review_in.product_id,
            )
        )
    )
    if review_exist_execute.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Review for product with id {review_in.product_id} from user with id {current_user.id} alredy exists",
        )

    new_review = ReviewModel(
        user_id=current_user.id,
        product_id=review_in.product_id,
        comment=review_in.comment,
        mark=review_in.mark,
    )

    session.add(new_review)
    await session.commit()

    review_out = ReviewOut.model_validate(new_review, from_attributes=True)
    return review_out


@router.patch(
    "/rewiew/{rewiew_id}",
    summary="Обновить отзыв к товару от пользователя",
    status_code=status.HTTP_200_OK,
)
@exception_handler
async def update_review(
    review_id: int,
    updated_review_in: ReviewUpdate,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> ReviewOut:

    review = await session.get(ReviewModel, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id {review_id} not found",
        )

    if updated_review_in.comment:
        review.comment = updated_review_in.comment
    if updated_review_in.mark:
        review.mark = updated_review_in.mark

    await session.commit()

    review_out = ReviewOut.model_validate(review, from_attributes=True)

    return review_out


@router.delete(
    "/review/{rewiew_id}",
    summary="Удаление отзыва к товару от пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
@exception_handler
async def delete_review(
    review_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> None:
    review_execute = await session.execute(
        delete(ReviewModel).where(ReviewModel.id == review_id)
    )

    if review_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {review_id} not found",
        )

    await session.commit()


@router.get(
    "/cart", summary="Просмотр товаров в корзине", status_code=status.HTTP_200_OK
)
@exception_handler
async def get_products_from_cart(
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
    limit: int = Query(
        default=10, ge=1, le=50, description="Количество товаров на странице"
    ),
    offset: int = Query(default=0, ge=0, description="Количество пропускаемых товаров"),
) -> list[ProductIdTitleMarkBrand]:

    products_in_cart_execute = await session.execute(
        select(
            ProductModel.id,
            ProductModel.title,
            ProductModel.brand,
            ProductModel.average_mark,
            CartModel.added_at,
        )
        .join(CartModel, CartModel.product_id == ProductModel.id)
        .where(CartModel.user_id == current_user.id)
        .order_by(CartModel.added_at.desc())
        .offset(offset)
        .limit(limit)
    )

    products_in_cart = products_in_cart_execute.mappings().all()
    if not products_in_cart:
        return []

    products_in_cart_out = [
        ProductIdTitleMarkBrand.model_validate(product, from_attributes=True)
        for product in products_in_cart
    ]
    return products_in_cart_out


@router.post(
    "/cart", summary="Добавление товара в корзину", status_code=status.HTTP_201_CREATED
)
@exception_handler
async def add_product_to_cart(
    cart_in: CartIn,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> CartOut:
    in_cart_exist_execute = await session.execute(
        select(
            exists().where(
                CartModel.user_id == current_user.id,
                CartModel.product_id == cart_in.product_id,
            )
        )
    )
    if in_cart_exist_execute.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {cart_in.product_id} already in user {current_user.id} cart",
        )

    new_product_in_cart = CartModel(
        user_id=current_user.id, product_id=cart_in.product_id, added_at=datetime.now()
    )

    session.add(new_product_in_cart)
    await session.commit()

    product_in_cart_out = CartOut.model_validate(
        new_product_in_cart, from_attributes=True
    )
    return product_in_cart_out


@router.delete(
    "/cart/{product_in_cart_id}",
    summary="Удаление товара из корзины",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product_from_cart(
    product_from_cart_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> None:
    product_in_cart_execute = await session.execute(
        delete(CartModel).where(CartModel.id == product_from_cart_id)
    )

    if product_in_cart_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product in cart with id {product_from_cart_id} found",
        )

    await session.commit()


@router.get(
    "/liked", summary="Просмотр понравившихся товаров", status_code=status.HTTP_200_OK
)
@exception_handler
async def get_liked_products(
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
    order: Literal["asc", "desc"] = Query(default="desc", description="Тип фильтрации"),
) -> list[ProductIdTitleMarkBrand]:

    liked_products_execute = await session.execute(
        select(
            ProductModel.id,
            ProductModel.title,
            ProductModel.brand,
            ProductModel.average_mark,
        )
        .join(LikedModel, LikedModel.product_id == ProductModel.id)
        .where(LikedModel.user_id == current_user.id)
        .order_by(LikedModel.added_at if order == "asc" else LikedModel.added_at.desc())
    )

    liked_products = liked_products_execute.mappings().all()
    if not liked_products:
        return []

    liked_products_out = [
        ProductIdTitleMarkBrand.model_validate(product, from_attributes=True)
        for product in liked_products
    ]
    return liked_products_out


@router.post(
    "/liked",
    summary="Добавление товара в понравившиеся",
    status_code=status.HTTP_201_CREATED,
)
@exception_handler
async def add_liked_product(
    liked_in: CartIn,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> CartOut:
    in_liked_exist_execute = await session.execute(
        select(
            exists().where(
                LikedModel.user_id == current_user.id,
                LikedModel.product_id == liked_in.product_id,
            )
        )
    )
    if in_liked_exist_execute.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {liked_in.product_id} already in user {current_user.id} cart",
        )

    new_liked_product = LikedModel(
        user_id=current_user.id, product_id=liked_in.product_id, added_at=datetime.now()
    )

    session.add(new_liked_product)
    await session.commit()

    liked_product_out = LikedOut.model_validate(new_liked_product, from_attributes=True)
    return liked_product_out


@router.delete(
    "/liked/{liked_product_id}",
    summary="Удаление товара из понравившихся",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_liked_product(
    liked_product_id: int,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> None:
    liked_product_execute = await session.execute(
        delete(LikedModel).where(CartModel.id == liked_product_id)
    )

    if liked_product_execute.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product in cart with id {liked_product_id} found",
        )

    await session.commit()


@router.post(
    "/order", summary="Оформление покупки товаров", status_code=status.HTTP_201_CREATED
)
@exception_handler
async def create_order(
    order_in: OrderSchema,
    session: SessionDep,
    current_user: CurrentUserSchema = Depends(decode_access_token),
) -> OrderOut:

    new_order = OrderModel(
        user_id=current_user.id,
        payment_status=PaymentStatusEnum.PENDING,
        delivery_status=DeliveryStatusEnum.PROCESSING,
        delivery_address=order_in.delivery_address,
        delivery_index=order_in.delivery_index,
    )
    promo_code = None
    if order_in.promo_code:
        promo_code_execute = await session.execute(
            select(PromoCodeModel).where(PromoCodeModel.code == order_in.promo_code)
        )
        promo_code = promo_code_execute.scalar_one_or_none()
        if promo_code:
            new_order.promo_code_id = promo_code.id

    session.add(new_order)
    await session.flush()

    products: list[ProductIdTitleMarkBrand] = []
    total_price = 0.0
    total_price_without_discount = 0.0
    for product in order_in.products:
        product_info = await session.get(ProductModel, product.product_id)
        if not product_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prodcut with id {product.product_id} not found",
            )
        total_price_without_discount += product_info.price
        total_price += product_info.price * (1 - product_info.discount / 100)

        new_order_product = OrderProductModel(
            order_id=new_order.id,
            product_id=product.product_id,
            price=product_info.price,
            discount=product_info.discount,
        )
        session.add(new_order_product)
        products.append(
            ProductIdTitleBrandPriceDiscount.model_validate(
                product_info, from_attributes=True
            )
        )
    if promo_code:
        total_price = total_price - (total_price * promo_code.discount / 100)

    new_order.total_price = total_price
    new_order.total_price_without_discount = total_price_without_discount

    payment_id, payment_url = await create_payment(
        new_order.total_price,
        "https://google.com",
        "Оплата товаров в electronic store",
        new_order.id,
        current_user.id,
    )

    new_order.payment_id = payment_id

    await session.commit()
    await session.refresh(new_order)

    order_out = OrderOut(
        id=new_order.id,
        user_id=new_order.user_id,
        total_price=new_order.total_price,
        total_price_without_discount=new_order.total_price_without_discount,
        payment_status=new_order.payment_status,
        delivery_status=new_order.delivery_status,
        delivery_address=new_order.delivery_address,
        delivery_index=new_order.delivery_index,
        products=products,
        promo_code_data=(
            PromoCodeSchema.model_validate(promo_code, from_attributes=True)
            if promo_code
            else None
        ),
        payment_url=payment_url,
    )

    return order_out
