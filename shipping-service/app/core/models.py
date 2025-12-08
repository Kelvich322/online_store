from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ShippingStatusEnum(StrEnum):
    SHIPPED = "SHIPPED"


class Shipments(BaseModel):
    id: str
    orderId: str
    status: ShippingStatusEnum
    trackingNumber: str
    created_at: datetime


class InboxShipments(BaseModel):
    id: str
    order_id: str
    payload: dict
    processed_at: datetime
