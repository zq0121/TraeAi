from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.auth import router as auth_router
from app.api.detection import router as detection_router
from app.api.files import router as files_router
from app.api.system import router as system_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models import *  # noqa: F401,F403
from app.services.init_service import initialize_database, init_storage

Base.metadata.create_all(bind=engine)
init_storage()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.mount("/results", StaticFiles(directory=str(settings.RESULT_DIR)), name="results")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(detection_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(files_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        initialize_database(db)
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "model_path": str(settings.MODEL_PATH), "model_exists": settings.MODEL_PATH.exists()}
