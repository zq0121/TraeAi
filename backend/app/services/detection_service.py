import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import cv2
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.detection import DefectCategory, DetectionRecord
from app.services.yolo_service import yolo_service
from app.utils.files import resolve_managed_path
from app.utils.image_processing import draw_detection_boxes_bgr, save_image


class DetectionService:
    @staticmethod
    def get_defect_categories(db: Session):
        return db.query(DefectCategory).order_by(DefectCategory.id).all()

    @staticmethod
    def get_category_for_detection(db: Session, det: dict) -> DefectCategory:
        class_id = det.get("model_class_id")
        name = det.get("category_name") or f"缺陷{class_id}"
        category = None
        if class_id is not None:
            category = db.query(DefectCategory).filter(DefectCategory.model_class_id == class_id).first()
        if not category:
            category = db.query(DefectCategory).filter(DefectCategory.name == name).first()
        if not category:
            # 如果数据库里没有对应类别，优先按名称创建，避免唯一约束冲突。
            category = db.query(DefectCategory).filter(DefectCategory.name == name).first()
        if not category:
            category = DefectCategory(model_class_id=class_id, name=name, color="#ef4444", description=f"自动识别类别：{name}")
            db.add(category)
            db.commit()
            db.refresh(category)
        elif category.model_class_id is None and class_id is not None:
            exists_same_id = db.query(DefectCategory).filter(DefectCategory.model_class_id == class_id, DefectCategory.id != category.id).first()
            if not exists_same_id:
                category.model_class_id = class_id
                db.commit()
                db.refresh(category)
        return category

    @staticmethod
    def enrich_detections(db: Session, detections: list[dict]) -> list[dict]:
        enriched = []
        for det in detections:
            category = DetectionService.get_category_for_detection(db, det)
            item = dict(det)
            item.update({
                "category_id": category.id,
                "category_name": category.name,
                "color": category.color,
            })
            enriched.append(item)
        return enriched

    @staticmethod
    def detect_image(db: Session, user_id: int, file_path: Path, original_name: str):
        started = time.perf_counter()
        result = yolo_service.detect_image(file_path)
        detections = DetectionService.enrich_detections(db, result["detections"])
        result_image = draw_detection_boxes_bgr(result["image_bgr"], detections)
        result_path = save_image(result_image, settings.RESULT_DIR)
        duration_ms = int((time.perf_counter() - started) * 1000)
        max_conf = max([d.get("confidence", 0) for d in detections], default=0)

        record = DetectionRecord(
            user_id=user_id,
            file_name=file_path.name,
            original_file_name=original_name,
            file_path=str(file_path),
            file_type=1,
            result_image_path=str(result_path),
            defect_count=len(detections),
            max_confidence=max_conf,
            defect_details=json.dumps(detections, ensure_ascii=False),
            duration_ms=duration_ms,
            status=1,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "success": True,
            "message": "图片检测完成",
            "defect_count": len(detections),
            "defects": detections,
            "result_image_path": str(result_path),
            "record_id": record.id,
            "duration_ms": duration_ms,
        }

    @staticmethod
    def detect_video(db: Session, user_id: int, file_path: Path, original_name: str):
        started = time.perf_counter()
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        result_path = settings.RESULT_DIR / f"result_{file_path.stem}.mp4"
        writer = cv2.VideoWriter(str(result_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

        all_detections = []
        last_detections = []
        frame_index = 0
        interval = max(1, int(settings.VIDEO_FRAME_INTERVAL))

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % interval == 0:
                detected = yolo_service.process_video_frame(frame)["detections"]
                last_detections = DetectionService.enrich_detections(db, detected)
                for item in last_detections:
                    item = dict(item)
                    item["frame_index"] = frame_index
                    all_detections.append(item)
            output_frame = draw_detection_boxes_bgr(frame, last_detections) if last_detections else frame
            writer.write(output_frame)
            frame_index += 1

        cap.release()
        writer.release()
        duration_ms = int((time.perf_counter() - started) * 1000)
        max_conf = max([d.get("confidence", 0) for d in all_detections], default=0)

        record = DetectionRecord(
            user_id=user_id,
            file_name=file_path.name,
            original_file_name=original_name,
            file_path=str(file_path),
            file_type=2,
            result_video_path=str(result_path),
            defect_count=len(all_detections),
            max_confidence=max_conf,
            defect_details=json.dumps(all_detections[:1000], ensure_ascii=False),
            duration_ms=duration_ms,
            status=1,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "success": True,
            "message": "视频检测完成",
            "defect_count": len(all_detections),
            "defects": all_detections[:200],
            "result_video_path": str(result_path),
            "record_id": record.id,
            "duration_ms": duration_ms,
        }

    @staticmethod
    def detect_camera_frame(db: Session, frame_bgr):
        started = time.perf_counter()
        result = yolo_service.process_video_frame(frame_bgr)
        detections = DetectionService.enrich_detections(db, result["detections"])
        return {
            "success": True,
            "message": "实时检测完成",
            "defect_count": len(detections),
            "defects": detections,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }

    @staticmethod
    def query_records(db: Session, user_id: int | None = None, file_type: int | None = None, category: str | None = None,
                      start_date: date | None = None, end_date: date | None = None, skip: int = 0, limit: int = 10):
        query = db.query(DetectionRecord)
        if user_id:
            query = query.filter(DetectionRecord.user_id == user_id)
        if file_type:
            query = query.filter(DetectionRecord.file_type == file_type)
        if start_date:
            query = query.filter(DetectionRecord.detection_time >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(DetectionRecord.detection_time < datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
        if category:
            query = query.filter(DetectionRecord.defect_details.like(f"%{category}%"))
        return query.order_by(DetectionRecord.detection_time.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_record(db: Session, record_id: int):
        return db.query(DetectionRecord).filter(DetectionRecord.id == record_id).first()

    @staticmethod
    def delete_record(db: Session, record: DetectionRecord):
        for path in [record.file_path, record.result_image_path, record.result_video_path]:
            if path:
                try:
                    managed = resolve_managed_path(path, [settings.UPLOAD_DIR, settings.RESULT_DIR])
                    managed.unlink(missing_ok=True)
                except Exception:
                    pass
        db.delete(record)
        db.commit()

    @staticmethod
    def format_record(record: DetectionRecord) -> dict:
        type_names = {1: "图片", 2: "视频", 3: "摄像头"}
        return {
            "id": record.id,
            "user_id": record.user_id,
            "username": record.user.username if record.user else "",
            "file_name": record.file_name,
            "original_file_name": record.original_file_name,
            "file_path": record.file_path,
            "file_type": record.file_type,
            "file_type_name": type_names.get(record.file_type, "未知"),
            "result_image_path": record.result_image_path,
            "result_video_path": record.result_video_path,
            "defect_count": record.defect_count,
            "max_confidence": record.max_confidence,
            "defect_details": record.defect_details,
            "detection_time": record.detection_time,
            "duration_ms": record.duration_ms,
            "status": record.status,
        }

    @staticmethod
    def get_statistics(db: Session) -> dict:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        records = db.query(DetectionRecord).all()
        total_detection = len(records)
        total_defects = sum(r.defect_count or 0 for r in records)
        today_records = [r for r in records if r.detection_time >= today_start]
        today_detection = len(today_records)
        today_defects = sum(r.defect_count or 0 for r in today_records)
        category_stats = DetectionService.get_category_statistics(db)
        return {
            "total_detection": total_detection,
            "total_defects": total_defects,
            "today_detection": today_detection,
            "today_defects": today_defects,
            "defect_rate": round(total_defects / total_detection, 2) if total_detection else 0,
            "category_stats": category_stats,
        }

    @staticmethod
    def get_category_statistics(db: Session) -> list[dict]:
        categories = db.query(DefectCategory).all()
        stats = {c.name: {"category_id": c.id, "category_name": c.name, "color": c.color, "count": 0} for c in categories}
        for record in db.query(DetectionRecord).all():
            try:
                details = json.loads(record.defect_details or "[]")
            except Exception:
                details = []
            for defect in details:
                name = defect.get("category_name", "其他")
                stats.setdefault(name, {"category_id": defect.get("category_id"), "category_name": name, "color": defect.get("color", "#64748b"), "count": 0})
                stats[name]["count"] += 1
        return list(stats.values())

    @staticmethod
    def get_trend(db: Session, days: int = 7) -> list[dict]:
        end = datetime.now().date()
        start = end - timedelta(days=days - 1)
        rows = []
        for i in range(days):
            day = start + timedelta(days=i)
            day_start = datetime.combine(day, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            records = db.query(DetectionRecord).filter(DetectionRecord.detection_time >= day_start, DetectionRecord.detection_time < day_end).all()
            rows.append({
                "date": day.isoformat(),
                "detection_count": len(records),
                "defect_count": sum(r.defect_count or 0 for r in records),
            })
        return rows
