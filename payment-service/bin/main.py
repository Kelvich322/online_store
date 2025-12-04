import asyncio

from app.application.container import ApplicationContainer

async def main():
    container = ApplicationContainer()
    container.config.from_yaml("app/config.yaml", required=True)

    process_inbox_events_use_case = container.process_inbox_events_use_case()

    kafka_consumer = container.infrastructure_container.kafka_consumer()

    await kafka_consumer.set_handler(process_inbox_events_use_case.handle_message)
    async with kafka_consumer:
        await kafka_consumer.consume_messages()

if __name__ == "__main__":
    asyncio.run(main())
