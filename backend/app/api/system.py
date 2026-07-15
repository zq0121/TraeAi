from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_admin_user
from app.core.database import get_db
from app.models.detection import SystemSetting
from app.models.user import LoginLog, OperationLog, User
from app.schemas.detection import SystemSettingResponse, SystemSettingUpdate
from app.schemas.user import RoleCreate, RoleResponse, RoleUpdate
from app.services.user_service import RoleService

router = APIRouter(prefix="/system", tags=["系统管理"])


@router.get("/roles", response_model=list[RoleResponse])
async def get_roles(db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    return RoleService.list_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(data: RoleCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    if RoleService.get_by_name(db, data.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色名称已存在")
    return RoleService.create_role(db, data)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    role = RoleService.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return RoleService.update_role(db, role, data)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    role = RoleService.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    db.delete(role)
    db.commit()


@router.get("/settings", response_model=list[SystemSettingResponse])
async def get_settings(db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    return db.query(SystemSetting).order_by(SystemSetting.id).all()


@router.put("/settings/{setting_key}", response_model=SystemSettingResponse)
async def update_setting(setting_key: str, data: SystemSettingUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    setting = db.query(SystemSetting).filter(SystemSetting.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设置项不存在")
    setting.setting_value = data.setting_value
    db.commit()
    db.refresh(setting)
    return setting


@router.get("/logs/login")
async def login_logs(db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    rows = db.query(LoginLog).order_by(LoginLog.login_time.desc()).limit(100).all()
    return [{"id": r.id, "username": r.username, "login_time": r.login_time, "login_ip": r.login_ip, "login_status": r.login_status, "user_agent": r.user_agent} for r in rows]


@router.get("/logs/operation")
async def operation_logs(db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)):
    rows = db.query(OperationLog).order_by(OperationLog.operation_time.desc()).limit(100).all()
    return [{"id": r.id, "user_id": r.user_id, "operation_type": r.operation_type, "operation_module": r.operation_module, "operation_desc": r.operation_desc, "operation_time": r.operation_time, "operation_ip": r.operation_ip} for r in rows]
