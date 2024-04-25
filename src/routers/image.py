from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.database import get_db_async

router = APIRouter(tags=["image"])


@router.post("/process_image/{pipeline_id}")
async def process_image(
    pipeline_id: int,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_async),
):
    pipeline = await db.get(models.Pipeline, pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found"
        )

    image_bytes = await image.read()

    return pipeline.tasks
