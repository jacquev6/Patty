import datetime
import os.path
import urllib.parse

import boto3
import botocore
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
        model_url = urllib.parse.urlparse(settings.IMAGES_DETECTION_MODEL_2025_09_15_URL)
        model_path = os.path.join(settings.IMAGES_DETECTION_MODELS_DIRECTORY_PATH, os.path.basename(model_url.path))
        if not os.path.isfile(model_path):
            log(f"Downloading images detection model from {model_url.geturl()} to {model_path}")
            s3 = boto3.client("s3", config=botocore.client.Config(region_name="eu-west-3"))
            s3.download_file(Bucket=model_url.netloc, Key=model_url.path[1:], Filename=model_path)
        log(f"Loading images detection model from {model_path}")
        model = ultralytics.models.YOLO(model_path)

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
        (
            f"{identifier_prefix}c{box_index}",
            int(box[0].item()),
            int(box[1].item()),
            int(box[2].item()),
            int(box[3].item()),
        )
        for box_index, box in enumerate(boxes_.xyxy)
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
