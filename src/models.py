from typing import Optional

from sqlalchemy import ForeignKey, String
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
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        init=False,
        nullable=False,
    )


class Pipeline(BaseModel):
    """
    Таблица для хранения пайплайнов
    """

    __tablename__ = "pipelines"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    tasks: Mapped[list["Task"]] = relationship(
        secondary="pipeline_tasks",
        lazy="subquery",
        order_by="PipelineTask.order",  # Сортируем по порядку в пайплайне
    )


class Task(BaseModel):
    """
    Таблица для хранения задач, из которых собираются пайплайны

    :param paprameters: параметры задачи
    """

    __tablename__ = "tasks"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    service: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )


class PipelineTask(Base):
    """
    Промежуточная таблица для связи пайплайнов и задач через связь M2M

    :param order: порядок выполнения задачи в пайплайне
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
