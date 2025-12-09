import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db_schema import InboxShipments, Shipments


class ShipmentsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> Shipments:
        new_shipments = Shipments(**data)
        self._session.add(new_shipments)
        await self._session.flush()
        return new_shipments


class InboxRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict[str, Any]) -> InboxShipments:
        new_inbox_shipment = InboxShipments(**data)
        self._session.add(new_inbox_shipment)
        await self._session.flush()
        return new_inbox_shipment

    async def get_by_id(self, order_id: str) -> InboxShipments | None:
        if isinstance(order_id, str):
            order_id = uuid.UUID(order_id)

        query = select(InboxShipments).where(InboxShipments.order_id == order_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
