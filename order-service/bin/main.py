import asyncio

import uvicorn
from fastapi import FastAPI

from app.application.container import ApplicationContainer
from app.presentation import api
from app.presentation.api import router
from app.presentation.container import PresentationContainer
from app.presentation.outbox_worker import OutboxWorker


def build_api(container: ApplicationContainer):
    app = FastAPI()
    app.include_router(router)
    container.wire(modules=[api])
    return app


async def main():
    presentation_container = PresentationContainer()
    presentation_container.config.from_yaml("app/config.yaml", required=True)

    app = build_api(presentation_container.application)
    worker: OutboxWorker = presentation_container.outbox_worker()
    kafka_consumer = (
        presentation_container.application.infrastructure_container.kafka_consumer()
    )
    handle_messages_use_case = (
        presentation_container.application.handle_message_use_case()
    )

    await kafka_consumer.set_handler(handle_messages_use_case.handle_message)

    async with kafka_consumer:
        await asyncio.sleep(2)
        api_task = asyncio.create_task(
            uvicorn.Server(
                uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
            ).serve()
        )

        worker_task = asyncio.create_task(worker.run())

        consumer_task = asyncio.create_task(kafka_consumer.consume_messages())

        await asyncio.gather(api_task, worker_task, consumer_task)


if __name__ == "__main__":
    asyncio.run(main())
