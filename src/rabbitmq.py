import json
from dataclasses import dataclass
from os import environ

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection


@dataclass
class RabbitConnection:
    connection: AbstractRobustConnection | None = None
    channel: AbstractRobustChannel | None = None

    def status(self) -> bool:
        """
        Checks if connection established

        :return: True if connection established
        """
        if self.connection.is_closed or self.channel.is_closed:
            return False
        return True

    async def _clear(self) -> None:
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()

        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        """
        Establish connection with the RabbitMQ

        :return: None
        """

        try:
            self.connection = await connect_robust(
                host=environ.get("RABBITMQ_HOST")
            )
            self.channel = await self.connection.channel(
                publisher_confirms=False
            )
        except Exception as e:
            await self._clear()
            print("RabbitMQ connection error: ", e)

    async def disconnect(self) -> None:
        """
        Disconnect and clear connections from RabbitMQ

        :return: None
        """
        await self._clear()

    async def send_messages(
        self,
        messages: list | dict,
        routing_key: str = "default",
    ) -> None:
        """
        Public message or messages to the RabbitMQ queue.

        :param messages: list or dict with messages objects.
        :param routing_key: Routing key of RabbitMQ queue.
        """
        if not self.channel:
            raise RuntimeError("RabbitMQ connection not established")

        if isinstance(messages, dict):
            messages = [messages]

        async with self.channel.transaction():
            for message in messages:
                message = Message(body=json.dumps(message).encode())

                await self.channel.default_exchange.publish(
                    message,
                    routing_key=routing_key,
                )


rabbit_connection = RabbitConnection()
