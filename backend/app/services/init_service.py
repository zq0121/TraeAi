import json

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.detection import DefectCategory, SystemSetting
from app.models.user import Role, User
from app.utils.files import ensure_directories
from app.utils.security import get_password_hash

COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4", "#8b5cf6", "#ec4899", "#64748b"]
FALLBACK_CATEGORIES = ["裂纹", "划痕", "夹杂", "氧化皮", "其他"]


def init_storage() -> None:
    ensure_directories(settings.UPLOAD_DIR, settings.RESULT_DIR, settings.STATIC_DIR)


def init_roles(db: Session) -> None:
    roles = [
        ("admin", "超级管理员", ["*"]),
        ("inspector", "检测员", ["detection", "records", "analysis", "files"]),
        ("user", "普通用户", ["detection", "records"]),
    ]
    for name, description, permissions in roles:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            db.add(Role(name=name, description=description, permissions=json.dumps(permissions, ensure_ascii=False)))
    db.commit()


def init_admin(db: Session) -> None:
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        db.add(User(
            username="admin",
            password=get_password_hash("admin123"),
            real_name="系统管理员",
            email="admin@example.com",
            role_id=admin_role.id if admin_role else None,
            status=1,
        ))
        db.commit()


def init_categories(db: Session) -> None:
    # 启动阶段不强制同步 YOLO 类别，避免旧数据库中的缺陷类别与模型类别冲突。
    # 真实模型类别会在首次检测时由检测服务按 model.names 自动映射/创建。
    if not db.query(DefectCategory).filter(DefectCategory.name == "其他").first():
        db.add(DefectCategory(model_class_id=None, name="其他", color="#64748b", description="未匹配缺陷类别"))
    db.commit()


def init_settings(db: Session) -> None:
    data = {
        "confidence_threshold": (str(settings.CONFIDENCE_THRESHOLD), "YOLO 检测置信度阈值"),
        "iou_threshold": (str(settings.IOU_THRESHOLD), "YOLO NMS IOU 阈值"),
        "max_upload_size": (str(settings.MAX_UPLOAD_SIZE), "最大上传文件大小"),
        "model_path": (str(settings.MODEL_PATH), "当前检测模型路径"),
    }
    for key, (value, desc) in data.items():
        if not db.query(SystemSetting).filter(SystemSetting.setting_key == key).first():
            db.add(SystemSetting(setting_key=key, setting_value=value, setting_desc=desc))
    db.commit()


def initialize_database(db: Session) -> None:
    init_storage()
    init_roles(db)
    init_admin(db)
    init_categories(db)
    init_settings(db)
