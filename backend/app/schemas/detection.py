from datetime import datetime
from pydantic import BaseModel


class DefectBox(BaseModel):
    model_class_id: int | None = None
    category_id: int | None = None
    category_name: str
    confidence: float
    bbox: list[int]
    area: int | None = None
    center: list[int] | None = None
    color: str = "#ef4444"


class DetectionResponse(BaseModel):
    success: bool
    message: str
    defect_count: int
    defects: list[DefectBox] = []
    result_image_path: str | None = None
    result_video_path: str | None = None
    record_id: int | None = None
    duration_ms: int | None = None


class DetectionRecordResponse(BaseModel):
    id: int
    user_id: int | None = None
    username: str | None = None
    file_name: str | None = None
    original_file_name: str | None = None
    file_path: str | None = None
    file_type: int
    file_type_name: str
    result_image_path: str | None = None
    result_video_path: str | None = None
    defect_count: int
    max_confidence: float | None = None
    defect_details: str | None = None
    detection_time: datetime
    duration_ms: int | None = None
    status: int

    class Config:
        from_attributes = True


class DefectCategoryResponse(BaseModel):
    id: int
    model_class_id: int | None = None
    name: str
    color: str
    description: str | None = None

    class Config:
        from_attributes = True


class CategoryStat(BaseModel):
    category_id: int | None = None
    category_name: str
    color: str
    count: int


class StatisticsResponse(BaseModel):
    total_detection: int
    total_defects: int
    today_detection: int
    today_defects: int
    defect_rate: float
    category_stats: list[CategoryStat]


class SystemSettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str | None = None
    setting_desc: str | None = None

    class Config:
        from_attributes = True


class SystemSettingUpdate(BaseModel):
    setting_value: str
