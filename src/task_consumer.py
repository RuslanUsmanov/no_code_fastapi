import asyncio
import json
import logging
from datetime import datetime
from os import environ

import aio_pika
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.database import SessionLocalAsync
from src.rabbitmq import rabbit_connection
from src.tasks import ai_model, preprocess, save_to_db

PARALLEL_TASKS = 10

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s"
)


async def message_router(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    """Обработчик сообщений

    :param aio_pika.abc.AbstractIncomingMessage message: Сообщение
    """

    # logging.debug(f"Received message: {message.body}")
    async with message.process():
        db: AsyncSession = SessionLocalAsync()

        body = json.loads(message.body.decode())

        task_run = await db.get(models.TaskRun, body["taskrun_id"])
        task_run.status = "running"

        db.add(task_run)
        await db.commit()

        try:
            # Выполняем текущую задачу
            match body["serivce_name"]:
                case "preprocess":
                    result = preprocess.preprocess_image(body["data"])
                case "ai_model":
                    result = ai_model.detect_auto(body["data"])
                case "save_to_db":
                    await save_to_db.save_detected_data(
                        db, body["data"], task_run.pipelinerun_id
                    )
                case _:
                    raise ValueError(
                        f"Service {body['service_name']} not found"
                    )
        except Exception as e:
            task_run.status = "failed"

            db.add(task_run)
            await db.commit()
            logging.error(e)
            await db.close()
            # TODO Еще пометить надо запуск пайплайна как фейлд
            return

        task_run.status = "finished"
        task_run.finished_at = datetime.now()

        db.add(task_run)
        await db.commit()

        next_task = await db.execute(
            select(models.TaskRun)
            .where(models.TaskRun.id > task_run.id)
            .order_by(models.TaskRun.id)
        )
        next_task = next_task.scalars().first()

        if next_task:
            # Если есть еще задачи в пайплайне, то передаем следующей задаче

            message = {
                "data": result,
                "taskrun_id": next_task.id,
                "serivce_name": next_task.task.service,
            }

            await rabbit_connection.connect()

            await rabbit_connection.send_messages(message)

            await rabbit_connection.disconnect()

        else:
            # Если нет задач в пайплайне, то помечаем пайплайн как завершенный
            pipline_run = await db.get(
                models.PipelineRun, task_run.pipelinerun_id
            )
            pipline_run.status = "finished"
            pipline_run.finished_at = datetime.now()
            db.add(pipline_run)
            await db.commit()
        await db.close()


async def main() -> None:
    """Запускает потоки обработки сообщений"""

    connection = await aio_pika.connect_robust(
        host=environ.get("RABBITMQ_HOST")
    )
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=PARALLEL_TASKS)
        queue = await channel.declare_queue("default", auto_delete=True)

        logging.info(" [*] Waiting for messages. To exit press CTRL+C")

        await queue.consume(message_router)

        try:
            await asyncio.Future()
        finally:
            await connection.close()


if __name__ == "__main__":
    logging.info("Starting task consumer")
    asyncio.run(main())
