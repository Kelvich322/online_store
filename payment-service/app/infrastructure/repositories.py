import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db_schema import InboxPayments, Payments


class PaymentsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> Payments:
        new_payment = Payments(**data)
        self._session.add(new_payment)
        await self._session.flush()
        return new_payment


class InboxRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> InboxPayments:
        new_inbox_payment = InboxPayments(**data)
        self._session.add(new_inbox_payment)
        await self._session.flush()
        return new_inbox_payment

    async def get_by_id(self, order_id: str) -> InboxPayments | None:
        if isinstance(order_id, str):
            order_id = uuid.UUID(order_id)

        query = select(InboxPayments).where(InboxPayments.order_id == order_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
