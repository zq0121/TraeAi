from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _font(size: int = 18):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_detection_boxes_bgr(image_bgr: np.ndarray, detections: list[dict]) -> np.ndarray:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(pil_image)
    font = _font(18)

    for det in detections:
        bbox = det.get("bbox") or [0, 0, 0, 0]
        x1, y1, x2, y2 = [int(v) for v in bbox]
        color = det.get("color") or "#ef4444"
        label = f"{det.get('category_name', '缺陷')} {det.get('confidence', 0):.2f}"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        text_bbox = draw.textbbox((x1, max(0, y1 - 24)), label, font=font)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x1, max(0, y1 - 24)), label, fill="white", font=font)

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def save_image(image_bgr: np.ndarray, result_dir: Path) -> Path:
    result_dir.mkdir(parents=True, exist_ok=True)
    path = result_dir / f"result_{uuid4().hex}.jpg"
    cv2.imwrite(str(path), image_bgr)
    return path
