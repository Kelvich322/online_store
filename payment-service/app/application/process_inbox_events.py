from pydantic import BaseModel

from app.application.create_payment import CreatePaymentUseCase, OrderDTO
from app.core.models import InboxPayments
from app.infrastructure.unit_of_work import UnitOfWork


class InboxDTO(BaseModel):
    order_id: str
    payload: dict


class ProcessInboxEventsUseCase:
    def __init__(
        self, unit_of_work: UnitOfWork, create_payment_use_case: CreatePaymentUseCase
    ):
        self._unit_of_work = unit_of_work
        self._create_payment_use_case = create_payment_use_case

    async def __call__(self, inbox_event: InboxDTO) -> InboxPayments:
        async with self._unit_of_work() as uow:
            existing_event = await uow.inbox.get_by_id(inbox_event.order_id)
            if existing_event:
                return existing_event

            payload = {"order_id": inbox_event.order_id, "payload": inbox_event.payload}

            inbox_event = await uow.inbox.create(payload)

            order_dto = OrderDTO(
                order_id=inbox_event.order_id, amount=inbox_event.payload["amount"]
            )
            await self._create_payment_use_case(order_dto)

            await uow.commit()
            return inbox_event

    async def handle_message(self, message: dict) -> None:
        inbox_event = InboxDTO(
            order_id=message["payload"]["id"], payload=message["payload"]
        )
        await self(inbox_event)
