from datetime import date
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.detection import DetectionRecordResponse, DetectionResponse, DefectCategoryResponse, StatisticsResponse
from app.services.detection_service import DetectionService
from app.utils.files import safe_filename, validate_extension

router = APIRouter(prefix="/detection", tags=["缺陷检测"])


async def save_upload(file: UploadFile, prefix: str, allowed: set[str]) -> Path:
    validate_extension(file.filename, allowed)
    filename = safe_filename(file.filename, prefix)
    path = settings.UPLOAD_DIR / filename
    size = 0
    with path.open("wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件超过大小限制")
            f.write(chunk)
    return path


@router.post("/image", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    path = await save_upload(file, "image", settings.ALLOWED_IMAGE_EXTENSIONS)
    try:
        return DetectionService.detect_image(db, current_user.id, path, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"图片检测失败：{exc}") from exc


@router.post("/video", response_model=DetectionResponse)
async def detect_video(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    path = await save_upload(file, "video", settings.ALLOWED_VIDEO_EXTENSIONS)
    try:
        return DetectionService.detect_video(db, current_user.id, path, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"视频检测失败：{exc}") from exc


@router.post("/camera/frame", response_model=DetectionResponse)
async def detect_camera_frame(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    validate_extension(file.filename or "frame.jpg", settings.ALLOWED_IMAGE_EXTENSIONS)
    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法解析摄像头帧")
    return DetectionService.detect_camera_frame(db, frame)


@router.get("/records", response_model=list[DetectionRecordResponse])
async def get_records(
    file_type: int | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = None if current_user.role and current_user.role.name == "admin" else current_user.id
    records = DetectionService.query_records(db, user_id, file_type, category, start_date, end_date, skip, limit)
    return [DetectionService.format_record(record) for record in records]


@router.get("/records/{record_id}", response_model=DetectionRecordResponse)
async def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = DetectionService.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="检测记录不存在")
    if (not current_user.role or current_user.role.name != "admin") and record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此记录")
    return DetectionService.format_record(record)


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = DetectionService.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="检测记录不存在")
    if (not current_user.role or current_user.role.name != "admin") and record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此记录")
    DetectionService.delete_record(db, record)


@router.get("/categories", response_model=list[DefectCategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    return DetectionService.get_defect_categories(db)


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return DetectionService.get_statistics(db)


@router.get("/statistics/category")
async def get_category_statistics(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return DetectionService.get_category_statistics(db)


@router.get("/statistics/trend")
async def get_trend(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return DetectionService.get_trend(db, days)
