from base64 import b64encode

import cv2
import numpy as np


def preprocess_image(image_bytes: bytes) -> bytes:
    decoded = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), -1)

    resized = cv2.resize(decoded, (640, 640))
    normed = cv2.normalize(
        resized, None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F
    )
    return b64encode(normed.tobytes())
