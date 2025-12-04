import uuid

from sqlalchemy import (
    DECIMAL,
    JSON,
    UUID,
    Column,
    DateTime,
    Text,
    func
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Payments(Base):
    __tablename__ = "ps_payments"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    order_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class InboxPayments(Base):
    __tablename__ = "ps_payments_inbox"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    order_id = Column(UUID(as_uuid=True), nullable=False)
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime, server_default=func.now())