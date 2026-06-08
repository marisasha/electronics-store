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
