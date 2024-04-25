import random


def detect_auto(image_bytes: bytes) -> list[float]:
    if random.random() > 0.5:
        return []

    x = random.randint(0, 640)
    y = random.randint(0, 640)
    width = random.randint(x, 640) - x
    height = random.randint(y, 640) - y

    return [x, y, width, height, random.random(), 1]
