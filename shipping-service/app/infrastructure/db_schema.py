import uuid

from app.infrastructure.utils import generate_ship_code

from sqlalchemy import (
    JSON,
    UUID,
    Column,
    DateTime,
    Text,
    func
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Shipments(Base):
    __tablename__ = "shipments"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    orderId = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Text, nullable=False)
    trackingNumber = Column(Text, nullable=False, default=generate_ship_code)
    created_at = Column(DateTime, server_default=func.now())


class InboxShipments(Base):
    __tablename__ = "shipments_inbox"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    order_id = Column(UUID(as_uuid=True), nullable=False)
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime, server_default=func.now())