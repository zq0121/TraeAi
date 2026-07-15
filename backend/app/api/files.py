from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.detection_service import DetectionService
from app.utils.files import resolve_managed_path

router = APIRouter(prefix="/files", tags=["文件管理"])


def check_file_permission(path: Path, db: Session, user: User) -> None:
    if user.role and user.role.name == "admin":
        return
    path_text = str(path)
    records = DetectionService.query_records(db, user_id=user.id, limit=1000)
    for record in records:
        if path_text in {record.file_path, record.result_image_path, record.result_video_path}:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此文件")


@router.get("/download/{file_path:path}")
async def download_file(file_path: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    path = resolve_managed_path(file_path, [settings.UPLOAD_DIR, settings.RESULT_DIR])
    check_file_permission(path, db, current_user)
    return FileResponse(path, filename=path.name)


@router.get("/preview/{file_path:path}")
async def preview_file(file_path: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    path = resolve_managed_path(file_path, [settings.UPLOAD_DIR, settings.RESULT_DIR])
    check_file_permission(path, db, current_user)
    return FileResponse(path)


@router.get("/list/images")
async def list_images(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = None if current_user.role and current_user.role.name == "admin" else current_user.id
    records = DetectionService.query_records(db, user_id=user_id, file_type=1, limit=1000)
    return [{"id": r.id, "file_name": r.original_file_name or r.file_name, "path": r.result_image_path, "source_path": r.file_path, "detection_time": r.detection_time} for r in records]


@router.get("/list/videos")
async def list_videos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = None if current_user.role and current_user.role.name == "admin" else current_user.id
    records = DetectionService.query_records(db, user_id=user_id, file_type=2, limit=1000)
    return [{"id": r.id, "file_name": r.original_file_name or r.file_name, "path": r.result_video_path, "source_path": r.file_path, "detection_time": r.detection_time} for r in records]
