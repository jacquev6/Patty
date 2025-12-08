# Copyright 2025 Mohamed-Amine Lasheb <mohamed-amine.lasheb@lecnam.net>
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import datetime

import cv2
import numpy as np
import PIL.Image
import ultralytics.models

from .. import settings


def log(message: str) -> None:
    # @todo Use actual logging
    print(datetime.datetime.now(), message, flush=True)


model: ultralytics.models.YOLO | None = None


def detect_images(
    identifier_prefix: str, input_pil_image: PIL.Image.Image
) -> tuple[PIL.Image.Image, dict[str, PIL.Image.Image]]:
    global model

    if model is None:
        log(f"Loading images detection model from {settings.IMAGES_DETECTION_MODEL_2025_09_15_PATH}")
        model = ultralytics.models.YOLO(settings.IMAGES_DETECTION_MODEL_2025_09_15_PATH)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2
    pad = 5
    black = (0, 0, 0)
    red = (0, 0, 255)
    white = (255, 255, 255)

    cv_image = cv2.cvtColor(np.array(input_pil_image), cv2.COLOR_RGB2BGR)

    boxes_ = model.predict(source=input_pil_image, verbose=False)[0].boxes
    assert boxes_ is not None
    boxes = [
        (f"{identifier_prefix}c{box_index + 1}", x1, y1, x2, y2)
        for box_index, (x1, y1, x2, y2) in enumerate(
            sorted(
                (
                    (int(box[0].item()), int(box[1].item()), int(box[2].item()), int(box[3].item()))
                    for box in boxes_.xyxy
                ),
                key=lambda box: (box[1], box[0]),
            )
        )
    ]
    detected_images: dict[str, PIL.Image.Image] = {}

    for identifier, x1, y1, x2, y2 in boxes:
        detected_images[identifier] = input_pil_image.crop((x1, y1, x2, y2))

    for identifier, x1, y1, x2, y2 in boxes:
        cv2.rectangle(cv_image, (x1, y1), (x2, y2), red, 3)

    overlay = cv_image.copy()

    text_positions: list[tuple[int, int]] = []
    for identifier, x1, y1, x2, y2 in boxes:
        (text_w, text_h), _ = cv2.getTextSize(identifier, font, font_scale, font_thickness)
        text_x = (x1 + x2 - text_w) // 2
        text_y = (y1 + y2 + text_h) // 2
        cv2.rectangle(overlay, (text_x - pad, text_y - text_h - pad), (text_x + text_w + pad, text_y + pad), black, -1)
        text_positions.append((text_x, text_y))

    alpha = 0.8
    cv_image = cv2.addWeighted(overlay, alpha, cv_image, 1 - alpha, 0)

    for (identifier, x1, y1, x2, y2), position in zip(boxes, text_positions):
        cv2.putText(cv_image, identifier, position, font, font_scale, white, font_thickness, cv2.LINE_AA)

    output_pil_image = PIL.Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

    return output_pil_image, detected_images
