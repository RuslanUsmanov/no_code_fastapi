from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.rabbitmq import rabbit_connection
from src.service.crud import create_pipline_run, create_task_run


async def create_and_run_pipeline(
    db: AsyncSession,
    pipeline_id: int,
    data: str,
) -> models.PipelineRun:
    """Создает запуск пайплайна и запускает задачи на испольнение через rabbit

    :param AsyncSession db: сессия БД
    :param int pipeline_id: идентификатор пайплайна
    :param str data: данные которые необходимо обработать
    :raises HTTPException: если пайплайн не найден
    :return models.PipelineRun: запущенный пайплайн
    """

    # Проверяем есть ли пайплайн с таким идентификатором
    pipeline = await db.get(models.Pipeline, pipeline_id)
    if not pipeline:
        # Если пайплайн не найден, то выбрасываем исключение
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found"
        )

    task_list = [task.id for task in pipeline.tasks]

    # Создаем запуск пайплайна
    pipeline_run = await create_pipline_run(db, pipeline_id)

    id_pipe_run = pipeline_run.id

    # Создаем задачи
    for task_id in task_list:
        await create_task_run(db, id_pipe_run, task_id)

    await db.refresh(pipeline_run)

    # Создаем сообщение для очереди
    message = {
        "data": data,
        "taskrun_id": pipeline_run.tasks[0].id,
        "serivce_name": pipeline_run.tasks[0].task.service,
    }

    # Отправляем сообщение в очередь
    await rabbit_connection.send_messages(messages=message)

    # Изменяем статус пайплайна
    pipeline_run.status = "running"

    db.add(pipeline_run)
    await db.commit()
    await db.refresh(pipeline_run)

    return pipeline_run
