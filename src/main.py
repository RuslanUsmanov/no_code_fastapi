from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.rabbitmq import rabbit_connection
from src.routers.image import router as image_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await rabbit_connection.connect()
    yield
    await rabbit_connection.disconnect()


app = FastAPI(
    title="No-code image processing service",
    version="0.1.0",
    description="REST API сервис, который принимает на вход изображения и "
    "прогоняет их по различным пайплайнам обработки изображений.",
    lifespan=lifespan,
)

app.include_router(image_router)
