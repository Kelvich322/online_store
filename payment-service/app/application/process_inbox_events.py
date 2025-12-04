from pydantic import BaseModel

from app.core.models import InboxPayments
from app.infrastructure.unit_of_work import UnitOfWork

class InboxDTO(BaseModel):
    order_id: str
    payload: dict


class ProcessInboxEventsUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def __call__(self, inbox_event: InboxDTO) -> InboxPayments:
        async with self._unit_of_work() as uow:
            payload = {
                "order_id": inbox_event.order_id,
                "payload": inbox_event.payload
            }

            inbox_event = await uow.inbox.create(payload)

            await uow.commit()
            return inbox_event