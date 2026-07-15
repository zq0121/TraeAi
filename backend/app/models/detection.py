from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class DefectCategory(Base):
    __tablename__ = "defect_categories"

    id = Column(Integer, primary_key=True, index=True)
    model_class_id = Column(Integer, unique=True, nullable=True, index=True)
    name = Column(String(80), unique=True, nullable=False, index=True)
    color = Column(String(20), default="#ef4444")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    file_name = Column(String(255))
    original_file_name = Column(String(255))
    file_path = Column(String(500))
    file_type = Column(Integer, default=1)
    result_image_path = Column(String(500))
    result_video_path = Column(String(500))
    defect_count = Column(Integer, default=0)
    max_confidence = Column(Float, default=0)
    defect_details = Column(Text, default="[]")
    detection_time = Column(DateTime, default=datetime.now, index=True)
    duration_ms = Column(Integer, default=0)
    status = Column(Integer, default=1)
    remark = Column(Text)

    user = relationship("User", back_populates="detection_records")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text)
    setting_desc = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
