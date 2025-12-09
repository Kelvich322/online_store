from pydantic import BaseModel

from app.infrastructure.unit_of_work import UnitOfWork
from app.core.models import OrderStatusEnum

class HandlerDTO(BaseModel):
    order_id: str
    status: OrderStatusEnum


class HandleMessagesUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def handle_message(self, handle_message: HandlerDTO):
        async with self._unit_of_work() as uow:
            order_status = await uow.orders.create_order_status(
                order_id=handle_message.order_id, status=handle_message.status
            )
            await uow.commit()
            return order_status