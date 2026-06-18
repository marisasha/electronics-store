from datetime import datetime
from decimal import Decimal


def get_html_content_for_email_verification(code: str, id: str, first_name: str):
    verification_url = f"http://127.0.0.1:8000/api/v1/users/verify-code?id={id}&code={code}&is_email_verification=true"
    html_content = f"""
        <html>
            <body>
                <h2>Добрый день, {first_name}!</h2>
                <p>Чтобы подтвердить вашу почту перейдите по следующей ссылке: </p>
                <p style="font-size: 20px; text-align: center; font-weight: bold; padding: 10px; background-color: #f0f0f0;">
                    {verification_url}
                </p>
                <p>Код действителен в течение 5 минут.</p>
                <p>Хорошего дня!</p>
            </body>
        </html>
        """
    return html_content


def get_html_content_for_user_authenticate(code: str, first_name: str):
    html_content = f"""
        <html>
            <body>
                <h2>Добрый день, {first_name}!</h2>
                <p>Для получения доступа введите следующий код:</p>
                <p style="font-size: 20px; text-align: center; font-weight: bold; padding: 10px; background-color: #f0f0f0;">
                    {code}
                </p>
                <p>Код действителен в течение 5 минут.</p>
                <p>Хорошего дня!</p>
            </body>
        </html>
        """
    return html_content


def get_html_content_for_move_report(move_count: int, move_list: list, first_name: str):

    move_list = "<br>".join([f"- {ml.description}" for ml in move_list])
    html_content = f"""
        <html>
            <body>
                <h2>Добрый день, {first_name}!</h2>
                <p>За сегоднешний день вы совершили {move_count} действий </p>
                <p>А именно</p>
                {move_list}
                <p>Хорошего дня!</p>
            </body>
        </html>
        """
    return html_content


def get_html_content_for_payment(
    order_id: int,
    amount: Decimal | float,
    payment_id: str,
    status: str = "pending",
    description: str = "",
) -> str:
    now = datetime.now()

    status_labels = {
        "paid": "Оплачено",
        "canceled": "Оплата не прошла",
    }

    status_text = status_labels.get(status, status)

    html_content = f"""
    <html>
        <body>
            <h2>Оплата заказа #{order_id}</h2>
            <p>Сумма: {float(amount):.2f} ₽</p>
            <p>Дата: {now.strftime("%d.%m.%Y %H:%M")}</p>
            <p>Описание: {description or f"Заказ №{order_id}"}</p>
            <p>Статус: {status_text}</p>
            <p>ID платежа: {payment_id}</p>
            <br>
            <p>Хорошего дня!</p>
        </body>
    </html>
    """

    return html_content
