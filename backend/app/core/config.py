from pathlib import Path


class Settings:
    PROJECT_NAME = "钢材表面缺陷智能识别与分析平台V1.0"
    API_V1_STR = "/api/v1"

    BASE_DIR = Path(__file__).resolve().parents[3]
    BACKEND_DIR = BASE_DIR / "backend"
    MODEL_PATH = BASE_DIR / "best.pt"
    UPLOAD_DIR = BACKEND_DIR / "uploads"
    RESULT_DIR = BACKEND_DIR / "results"
    STATIC_DIR = BACKEND_DIR / "app" / "static"
    DATABASE_URL = f"sqlite:///{BACKEND_DIR / 'steel_defect.db'}"

    SECRET_KEY = "steel-defect-platform-change-me"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

    CONFIDENCE_THRESHOLD = 0.35
    IOU_THRESHOLD = 0.45
    MAX_UPLOAD_SIZE = 1024 * 1024 * 200
    VIDEO_FRAME_INTERVAL = 5

    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}

    CORS_ORIGINS = ["*"]


settings = Settings()
