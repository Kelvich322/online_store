import random
from decimal import Decimal

from pydantic import BaseModel

from app.core.models import PaymentStatusEnum, Payment
from app.infrastructure.unit_of_work import UnitOfWork
from app.infrastructure.kafka_producer import KafkaProducer


class OrderDTO(BaseModel):
    order_id: str
    amount: Decimal


class CreatePaymentUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        kafka_producer: KafkaProducer

    ):
        self._unit_of_work = unit_of_work
        self._kafka_producer = kafka_producer

    async def __call__(self, order: OrderDTO) -> Payment:
        async with self._kafka_producer as kp:
            async with self._unit_of_work() as uow:

                if random.randint(1, 999) % 2 == 1:
                    status = PaymentStatusEnum.PAID
                else:
                    status = PaymentStatusEnum.CANCELLED
                
                payload = {
                    "order_id": order.order_id,
                    "amount": str(order.amount),
                    "status": status
                }

                payment = await uow.payments.create(payload)

                try:
                    await kp.send_message(
                        topic=status.topic,
                        message={
                            "event_type": status,
                            "payload": payload,
                            "created_at": payment.created_at.isoformat()
                        }
                    )
                except Exception as e:
                    print(f"Failed to payment order {order.order_id} and send event {payment.id}: {e}")

                await uow.commit()
                return payment

