from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, TokenResponse, UserResponse
from app.services.user_service import UserService
from app.utils.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["认证"])


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "",
        status=user.status,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")
    try:
        user = UserService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            UserService.create_login_log(db, form_data.username, None, False, client_ip, user_agent)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        if user.status != 1:
            UserService.create_login_log(db, form_data.username, user.id, False, client_ip, user_agent)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已被禁用")
        user.last_login_at = datetime.now()
        user.last_login_ip = client_ip
        db.commit()
        UserService.create_login_log(db, user.username, user.id, True, client_ip, user_agent)
        token = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        return TokenResponse(access_token=token, user=to_user_response(user))
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"登录服务异常：{exc}") from exc


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return to_user_response(current_user)


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码不正确")
    current_user.password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}
