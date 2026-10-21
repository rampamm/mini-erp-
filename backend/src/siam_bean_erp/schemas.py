from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

Money = Annotated[Decimal, PlainSerializer(lambda v: f"{v:.2f}", return_type=str, when_used="json")]


def check_money(value: Decimal, label: str) -> Decimal:
    if not value.is_finite():
        raise ValueError(f"{label} must be a number")
    if value < 0:
        raise ValueError(f"{label} cannot be below 0")
    if value != value.quantize(Decimal("0.01")):
        raise ValueError(f"{label} can have at most 2 decimals")
    return value
