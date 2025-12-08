from pydantic import BaseModel

from app.core.models import InboxShipments
from app.infrastructure.unit_of_work import UnitOfWork
from app.application.create_shipment import CreateShipmentUseCase, OrderDTO

class InboxDTO(BaseModel):
    order_id: str
    payload: dict


class ProcessInboxEventsUseCase:
    def __init__(self, unit_of_work: UnitOfWork, create_payment_use_case: CreateShipmentUseCase):
        self._unit_of_work = unit_of_work
        self._create_shipment_use_case = create_payment_use_case

    async def __call__(self, inbox_event: InboxDTO) -> InboxShipments:
        async with self._unit_of_work() as uow:
            existing_event = await uow.inbox.get_by_id(inbox_event.order_id)
            if existing_event:
                return existing_event

            payload = {
                "order_id": inbox_event.order_id,
                "payload": inbox_event.payload
            }

            inbox_event = await uow.inbox.create(payload)

            order = OrderDTO(orderId=inbox_event.order_id)
            await self._create_shipment_use_case(order)

            await uow.commit()
            return inbox_event

    async def handle_message(self, message: dict) -> None:
        inbox_event = InboxDTO(order_id=message["orderId"], payload=message)
        await self(inbox_event)