from enum import Enum


class RoleEnum(str, Enum):
    USER = "USER"
    SALESCLERK = "SALESCLERK"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"

    def __str__(self):
        return self.value


class GenderEnum(str, Enum):
    Male = "M"
    Female = "F"

    def __str__(self):
        return self.value


class OrderStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

    def __str__(self):
        return self.value


class OperationEnum(str, Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"

    def __str__(self):
        return self.value
