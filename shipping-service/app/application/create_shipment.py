from pydantic import BaseModel

from app.core.models import ShippingStatusEnum, Shipments
from app.infrastructure.unit_of_work import UnitOfWork
from app.infrastructure.kafka_producer import KafkaProducer


class OrderDTO(BaseModel):
    orderId: str
    

class CreateShipmentUseCase:
    def __init__(
            self,
            unit_of_work: UnitOfWork,
            kafka_producer: KafkaProducer
    ):
        self._unit_of_work = unit_of_work
        self._kafka_producer = kafka_producer

    async def __call__(self, order: OrderDTO) -> Shipments:
        async with self._kafka_producer as kp:
            async with self._unit_of_work() as uow:

                payload = {
                    "orderId": order.orderId,
                    "status": ShippingStatusEnum.SHIPPED
                }

                shipment = await uow.shipments.create(payload)

                try:
                    await kp.send_message(
                        message={
                            "orderId": shipment.orderId,
                            "status": shipment.status,
                            "trackingNumber": shipment.trackingNumber,
                            "created_at": shipment.created_at.isoformat()
                        }
                    )
                except Exception as e:
                    print(f"Failed to shipment order {order.orderId} and send event {shipment.id}: {e}")
                
                await uow.commit()
                return shipment

