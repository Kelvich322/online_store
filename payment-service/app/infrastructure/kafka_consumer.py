import asyncio
import json
from typing import Any, Awaitable, Callable, Optional

from aiokafka import AIOKafkaConsumer, ConsumerRecord


class KafkaConsumer:
    def __init__(
            self,
            bootstrap_servers: str,
            topic: str,
            enable_auto_commit: bool,
            auto_offset_reset: str = "earliest",
            max_poll_records: int = 10,
            max_poll_interval_ms: int = 3000,
    ):
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._enable_auto_commit = enable_auto_commit
        self._auto_offset_reset = auto_offset_reset
        self._max_poll_records = max_poll_records
        self._max_poll_interval_ms = max_poll_interval_ms
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._handler: Optional[Callable] = None
        self._is_running: bool = False

    async def start(self) -> None:
        if self._consumer is not None:
            raise RuntimeError("Consumer is already started")
        
        if not self._handler:
            raise RuntimeError("Message handler is not set. Call set_handler() first")

        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            auto_offset_reset=self._auto_offset_reset,
            enable_auto_commit=self._enable_auto_commit,
            max_poll_records=self._max_poll_records,
            max_poll_interval_ms=self._max_poll_interval_ms,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else None,
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )
        await self._consumer.start()
        self._is_running = True

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            self._is_running = False

    async def set_handler(self, handler: Callable[[Any], Awaitable[None]]) -> None:
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("Handler must be an async function")
        
        self._handler = handler

    async def consume_messages(self) -> None:
        if not self._consumer:
            raise RuntimeError("Consumer is not started. Call start() first")

        while self._is_running:
            try:
                batch = await self._consumer.getmany(
                    timeout_ms=1000,
                    max_records=self._max_poll_records
                )

                if not batch:
                    print("Messages not found")
                    continue

                for tp, messages in batch.items():
                    for message in messages:
                        await self._process_message(message)
                        
            except Exception as e:
                    print(f"Error in consumption loop: {e}")
                    await asyncio.sleep(1)

    async def _process_message(self, message: ConsumerRecord) -> None:
        value = message.value

        if value is None:
            return
        
        await self._handler(value)       

    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()