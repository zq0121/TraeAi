from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from app.core.config import settings


class YOLOService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
            cls._instance.names = {}
        return cls._instance

    def load_model(self, model_path: str | Path | None = None):
        model_path = Path(model_path or settings.MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        self.model = YOLO(str(model_path))
        raw_names = getattr(self.model, "names", {}) or {}
        self.names = {int(k): str(v) for k, v in raw_names.items()} if isinstance(raw_names, dict) else {i: str(v) for i, v in enumerate(raw_names)}
        return True

    def get_names(self) -> dict[int, str]:
        if self.model is None:
            self.load_model()
        return self.names

    def _detect_rgb(self, image_rgb: np.ndarray, conf_threshold: float, iou_threshold: float) -> list[dict]:
        if self.model is None:
            self.load_model()
        results = self.model(image_rgb, conf=conf_threshold, iou=iou_threshold, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                detections.append({
                    "model_class_id": class_id,
                    "category_name": self.names.get(class_id, f"缺陷{class_id}"),
                    "confidence": round(confidence, 4),
                    "bbox": [x1, y1, x2, y2],
                    "area": max(0, x2 - x1) * max(0, y2 - y1),
                    "center": [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                })
        return detections

    def detect_image(self, image_path: str | Path, conf_threshold: float | None = None, iou_threshold: float | None = None) -> dict:
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            raise ValueError(f"无法读取图片: {image_path}")
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        detections = self._detect_rgb(image_rgb, conf_threshold or settings.CONFIDENCE_THRESHOLD, iou_threshold or settings.IOU_THRESHOLD)
        return {"image_bgr": image_bgr, "detections": detections}

    def process_video_frame(self, frame_bgr: np.ndarray, conf_threshold: float | None = None, iou_threshold: float | None = None) -> dict:
        image_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        detections = self._detect_rgb(image_rgb, conf_threshold or settings.CONFIDENCE_THRESHOLD, iou_threshold or settings.IOU_THRESHOLD)
        return {"frame_bgr": frame_bgr, "detections": detections}


yolo_service = YOLOService()
