from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class BaseModel(Base):
    """Базовая модель для таблиц"""

    __abstract__ = True
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        init=False,
        nullable=False,
    )


class Pipeline(BaseModel):
    """Таблица для хранения пайплайнов"""

    __tablename__ = "pipelines"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    tasks: Mapped[list["Task"]] = relationship(
        secondary="pipeline_tasks",
        lazy="immediate",
        order_by="PipelineTask.order",  # Сортируем по порядку в пайплайне
    )


class Task(BaseModel):
    """Таблица для хранения задач, из которых собираются пайплайны"""

    __tablename__ = "tasks"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )


class PipelineTask(Base):
    """Промежуточная таблица для связи пайплайнов и задач через связь M2M

    :param int order: порядок выполнения задачи в пайплайне
    """

    __tablename__ = "pipeline_tasks"
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), primary_key=True
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    order: Mapped[int] = mapped_column(nullable=False)


class PipelineRun(BaseModel):
    """Таблица для хранения запусков пайплайнов"""

    __tablename__ = "pipeline_runs"
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )
    result: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)

    tasks: Mapped[list["TaskRun"]] = relationship(lazy="immediate", init=False)


class TaskRun(BaseModel):
    """Таблица для хранения запусков задач"""

    __tablename__ = "task_runs"
    pipelinerun_id: Mapped[int] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"), nullable=False
    )
    status: Mapped[str] = mapped_column(nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )

    task: Mapped["Task"] = relationship(init=False, lazy="immediate")
