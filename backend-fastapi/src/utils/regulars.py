import re


def is_valid_email(email: str) -> bool:
    """
    Проверяет корректность email адреса.
    """
    # Регулярное выражение для проверки email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not email or not isinstance(email, str):
        return False

    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Проверяет корректность российского номера телефона.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    if not re.match(r"^\+?\d+$", cleaned):
        return False

    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    if len(cleaned) != 11:
        return False

    if not cleaned.startswith(("7", "8")):
        return False

    return True
