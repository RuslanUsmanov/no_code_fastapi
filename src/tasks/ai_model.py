import random
from base64 import b64decode


def detect_auto(image_bytes: str) -> list[float]:
    """Имитация работы ИИ-модели по обнаружению авто на изображении

    :param str image_bytes: изображение
    :return list[float]: список с результатами обнаружения
    """
    image = b64decode(image_bytes.encode())

    if random.random() > 0.5:
        return []

    x = random.randint(0, 640)
    y = random.randint(0, 640)
    width = random.randint(x, 640) - x
    height = random.randint(y, 640) - y

    return [x, y, width, height, random.random(), 1]
