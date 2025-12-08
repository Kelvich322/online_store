from dependency_injector import containers, providers

from app.application.create_shipment import CreateShipmentUseCase
from app.application.process_inbox_events import ProcessInboxEventsUseCase
from app.infrastructure.container import InfrastructureContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    infrastructure_container = providers.Container[InfrastructureContainer](
        InfrastructureContainer,
        config=config.infrastructure,
    )

    create_payment_use_case = providers.Singleton[CreateShipmentUseCase](
        CreateShipmentUseCase,
        unit_of_work=infrastructure_container.unit_of_work,
        kafka_producer=infrastructure_container.kafka_producer,
    )
    process_inbox_events_use_case = providers.Singleton[ProcessInboxEventsUseCase](
        ProcessInboxEventsUseCase,
        unit_of_work=infrastructure_container.unit_of_work,
        create_payment_use_case=create_payment_use_case,
    )
