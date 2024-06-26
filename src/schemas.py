from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Status(str, Enum):
    """Состояния пайплайнов и задач"""

    pending = "pending"
    running = "running"
    finished = "finished"
    failed = "failed"


class PipelineBase(BaseModel):
    name: str
    description: str


class Pipeline(PipelineBase):
    id: int
    tasks: list["Task"]

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    name: str
    service: str
    parameters: str | None = None


class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True


class TaskRun(BaseModel):
    """Запуски задач по конкретному запуску пайплайна"""

    id: int
    pipelinerun_id: int
    task_id: int
    status: Status
    started_at: datetime
    finished_at: datetime | None
    task: Task

    class Config:
        from_attributes = True


class PipelineRun(BaseModel):
    """Запуски пайплайнов"""

    pipeline_id: int
    id: int
    status: Status
    started_at: datetime
    finished_at: datetime | None
    result: str | None

    tasks: list[TaskRun]

    class Config:
        from_attributes = True
