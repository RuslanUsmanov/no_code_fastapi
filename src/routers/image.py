from base64 import b64encode

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src import schemas
from src.database import get_db_async
from src.service import runner

router = APIRouter(tags=["image"])


@router.post(
    "/process_image/{pipeline_id}", response_model=schemas.PipelineRun
)
async def process_image(
    pipeline_id: int,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_async),
):
    """Обработка изображения по указанному пайплайну"""

    image = await image.read()

    image_bytes = b64encode(image).decode()

    return await runner.create_and_run_pipeline(db, pipeline_id, image_bytes)
