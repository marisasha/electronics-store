from yookassa import Configuration, Payment  # type: ignore
import uuid
from src.config import settings

Configuration.configure(
    account_id=settings.yookassa.shop_id, secret_key=settings.yookassa.secret_key
)


async def create_payment(
    payment_amount: float,
    return_url: str,
    description: str,
    order_id: int,
    user_id: int,
) -> tuple[str, str]:
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {"value": payment_amount, "currency": "RUB"},
            "payment_method_data": {"type": "bank_card"},
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "description": description,
        },
        idempotence_key,
    )

    confirmation_url = payment.confirmation.confirmation_url
    return payment.id, confirmation_url


async def get_payment(payment_id: str) -> dict:
    payment = Payment.find_one(payment_id)
    return payment


async def capture_payment(payment_id: str, amount_value: float) -> None:
    idempotence_key = str(uuid.uuid4())
    response = Payment.capture(
        payment_id,
        {"amount": {"value": amount_value, "currency": "RUB"}},
        idempotence_key,
    )
