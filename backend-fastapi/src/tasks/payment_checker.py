import asyncio
from sqlalchemy import select

from src.sales_panel.models import ProductModel
from src.celery_app import celery_app
from src.logger import logger
from src.store.models import *
from src.database import get_celery_session
from src import youkassa
from src.tasks.email_sender import send_email
from src.user.models import UserModel
from src.utils.html_content import get_html_content_for_payment


def get_or_create_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@celery_app.task(
    bind=True,
    name="payment_checker",
    queue="payment",
    max_retries=3,
    default_retry_delay=60,
)
def check_payment(self):
    loop = get_or_create_loop()
    return loop.run_until_complete(run_check_payment(self))


async def run_check_payment(self):
    """
    Основная асинхронная логика выполнения задачи.
    """
    try:
        async with get_celery_session() as session:
            result = await session.execute(
                select(OrderModel).where(OrderModel.payment_status == "PENDING")
            )
            pending_orders = result.scalars().all()

            if not pending_orders:
                return {"status": "Pending orders not detected"}

            for order in pending_orders:
                if not order.payment_id:
                    logger.warning(f"Order {order.id} has no payment_id")
                    continue

                try:
                    payment_info = await youkassa.get_payment(order.payment_id)
                except Exception as e:
                    logger.error(f"Error getting payment {order.payment_id}: {e}")
                    continue

                if not payment_info:
                    logger.error(f"Payment {order.payment_id} not found")
                    continue

                if (
                    payment_info.status == "waiting_for_capture"
                    and payment_info.paid == True
                ):
                    # Получаем товары заказа
                    products_result = await session.execute(
                        select(OrderProductModel).where(
                            OrderProductModel.order_id == order.id
                        )
                    )
                    order_products = products_result.scalars().all()

                    if not order_products:
                        logger.warning(f"Order {order.id} has no products")
                        async with session.begin():
                            order.payment_status = "FAILED"
                        continue

                    # Проверяем наличие всех товаров
                    out_of_stock = False
                    products_to_update = []

                    for order_product in order_products:
                        product_info = await session.get(
                            ProductModel, order_product.product_id
                        )

                        if not product_info:
                            logger.error(
                                f"Product {order_product.product_id} not found"
                            )
                            out_of_stock = True
                            break

                        if product_info.stock_quantity <= 0:
                            logger.warning(f"Product {product_info.id} out of stock")
                            out_of_stock = True
                            break

                        products_to_update.append(product_info)

                    # Если товара нет - НЕ подтверждаем платеж!
                    if out_of_stock:
                        async with session.begin():
                            order.payment_status = "FAILED"
                        logger.warning(
                            f"Order {order.id} marked as FAILED due to out of stock"
                        )
                        continue  # <-- Пропускаем платеж!

                    # ТОЛЬКО ЕСЛИ товары есть - подтверждаем платеж
                    try:
                        await youkassa.capture_payment(
                            order.payment_id, order.total_price
                        )
                        logger.info(
                            f"Payment {order.payment_id} captured successfully\n=-=-=-=-=-===-=-=-=-=-=-=-=-===-"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to capture payment {order.payment_id}: {e}"
                        )
                        raise  # Если платеж не прошел - прерываем

                    # Обновляем БД

                    for product in products_to_update:
                        product.stock_quantity -= 1
                    order.payment_status = "PAID"

                    await session.commit()

                    user = await session.get(UserModel, order.user_id)

                    # Отправляем email
                    if user:
                        message = get_html_content_for_payment(
                            order.id,
                            order.total_price,
                            order.payment_id,
                            "paid",
                            "Оплата товаров в electronic store",
                        )
                        data_for_email = {
                            "email": user.email,
                            "subject": "Результаты платежа",
                            "message": message,
                        }
                        send_email.delay(data_for_email)
                    else:
                        logger.error(
                            f"User {order.user_id} not found for order {order.id}"
                        )

                    logger.info(f"Order {order.id} processed successfully")
                if product_info.status == "succeeded" and product_info.paid == "paid":
                    order.payment_status = "PAID"
                    await session.commit()
                if product_info.status == "canceled":
                    logger.warning(f"Payment {order.payment_id} was canceled")
                    order.payment_status = "FAILED"
                    await session.commit()
                    user = await session.get(UserModel, order.user_id)
                    if user:
                        message = get_html_content_for_payment(
                            order.id,
                            order.total_price,
                            order.payment_id,
                            "canceled",
                            "Оплата товаров в electronic store",
                        )
                        send_email.delay(
                            {
                                "email": user.email,
                                "subject": "Платёж отменён",
                                "message": message,
                            }
                        )

    except Exception as e:
        logger.error(f"Error in payment_checker: {e}", exc_info=True)
        raise
