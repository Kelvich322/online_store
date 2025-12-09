import asyncio
import json
from typing import Any, Awaitable, Callable, Optional, List

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from app.core.models import OrderStatusEnum
from app.application.handle_messages_use_case import HandlerDTO


class KafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        topics: List[str],
        enable_auto_commit: bool,
        auto_offset_reset: str = "earliest",
        max_poll_records: int = 10,
        max_poll_interval_ms: int = 3000,
    ):
        self._bootstrap_servers = bootstrap_servers
        self._topics = topics
        self._enable_auto_commit = enable_auto_commit
        self._auto_offset_reset = auto_offset_reset
        self._max_poll_records = max_poll_records
        self._max_poll_interval_ms = max_poll_interval_ms
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._handler: Optional[Callable[[Any], Awaitable[None]]] = None
        self._is_running: bool = False

    async def start(self) -> None:
        print(f"🔧 DEBUG: Starting consumer for topics: {self._topics}")
        print(f"🔧 DEBUG: Handler is {'set' if self._handler else 'NOT set'}")  # TODO: Заменить на логер

        if self._consumer is not None:
            raise RuntimeError("Consumer is already started")
        
        if not self._handler:
            raise RuntimeError("Message handler is not set. Call set_handler() first")

        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            # group_id="multi-topic-consumer-group",
            auto_offset_reset=self._auto_offset_reset,
            session_timeout_ms=10000,
            heartbeat_interval_ms=3000,
            metadata_max_age_ms=5000,
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
                    continue

                for tp, messages in batch.items():
                    topic = tp.topic
                    for message in messages:
                        print(f"Start processing message from topic '{topic}': {message}") # TODO: Заменить на логер
                        await self._process_message(message)
                        
            except Exception as e:
                print(f"Error in consumption loop: {e}")  # TODO: Заменить на логер
                await asyncio.sleep(1)

    async def _process_message(self, message: ConsumerRecord) -> None:
        value = message.value

        if value is None:
            return
        try:
            message = HandlerDTO(
                order_id=value["orderId"],
                status=OrderStatusEnum(value["status"])
            )

            await self._handler(message)
        except Exception:
            raise

    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()