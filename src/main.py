from fastapi import FastAPI

from src.routers.image import router as image_router

app = FastAPI(
    title="No-code image processing service",
    version="0.1.0",
    description="REST API сервис, который принимает на вход изображения и "
    "прогоняет их по различным пайплайнам обработки изображений.",
)

app.include_router(image_router)
