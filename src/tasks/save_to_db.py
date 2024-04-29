from sqlalchemy.ext.asyncio import AsyncSession

from src import models


async def save_detected_data(
    db: AsyncSession, data: any, piplinerun_id: int
) -> None:
    """Сохранение результатов работы пайплайна в БД

    :param AsyncSession db: сессия БД
    :param any data: данные которые надо сохранить
    :param int piplinerun_id: идентификатор пайплайна
    :return: None
    """
    piplinerun = await db.get(models.PipelineRun, piplinerun_id)

    piplinerun.result = str(data)
    db.add(piplinerun)
    await db.commit()
    return None
