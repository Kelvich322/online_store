from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class PaymentStatusEnum(StrEnum):
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Payment(BaseModel):
    id: str
    order_id: str
    amount: Decimal
    status: PaymentStatusEnum
    created_at: datetime


class InboxPayments(BaseModel):
    id: str
    order_id: str
    payload: dict
    processed_at: datetime