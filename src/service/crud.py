from sqlalchemy.ext.asyncio import AsyncSession

from src import models


async def create_pipline_run(
    db: AsyncSession, pipeline_id: int
) -> models.PipelineRun:
    """Создает запуск пайплайна

    :param AsyncSession db: сессия БД
    :param int pipeline_id: идентификатор пайплайна
    :return models.PipelineRun: созданный пайплайн
    """
    pipeline_run = models.PipelineRun(
        pipeline_id=pipeline_id, status="pending"
    )
    db.add(pipeline_run)
    await db.commit()
    await db.refresh(pipeline_run)
    return pipeline_run


async def create_task_run(
    db: AsyncSession, pipeline_run_id: int, task_id: int
) -> models.TaskRun:
    """Создает запуск задачи

    :param AsyncSession db: сессия БД
    :param int pipeline_run_id: идентификатор запуска пайплайна
    :param int task_id: идентификатор задачи
    :return models.TaskRun: созданный запуск задачи
    """
    task_run = models.TaskRun(
        pipelinerun_id=pipeline_run_id, task_id=task_id, status="pending"
    )
    db.add(task_run)
    await db.commit()
    await db.refresh(task_run)
    return task_run
