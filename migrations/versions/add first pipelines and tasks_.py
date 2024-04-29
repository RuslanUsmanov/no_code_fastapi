"""empty message

Revision ID: add first pipelines and tasks
Revises: 23093a25a828
Create Date: 2024-04-29 23:32:04.406583

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session

from src.models import Pipeline, PipelineTask, Task

# revision identifiers, used by Alembic.
revision: str = "add first pipelines and tasks"
down_revision: Union[str, None] = "23093a25a828"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    db = Session(bind=bind)

    preproc = Task(name="preprocess", service="preprocess", parameters="{}")
    ai_model = Task(name="ai_model", service="ai_model", parameters="{}")
    save_to_db = Task(name="save_to_db", service="save_to_db", parameters="{}")

    db.add_all([preproc, ai_model, save_to_db])
    db.flush()

    db.refresh(preproc)
    db.refresh(ai_model)
    db.refresh(save_to_db)

    pipeline = Pipeline(
        name="first_pipeline", description="pipline for test", tasks=[]
    )

    db.add(pipeline)
    db.flush()

    db.refresh(pipeline)

    pipeline_tasks = [
        PipelineTask(pipeline_id=pipeline.id, task_id=preproc.id, order=0),
        PipelineTask(pipeline_id=pipeline.id, task_id=ai_model.id, order=1),
        PipelineTask(pipeline_id=pipeline.id, task_id=save_to_db.id, order=2),
    ]

    db.add_all(pipeline_tasks)
    db.commit()
    db.close()


def downgrade() -> None:
    pass
