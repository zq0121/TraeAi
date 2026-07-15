import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or payload.get("sub") is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or user.status != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


def require_permission(permission: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role and current_user.role.name == "admin":
            return current_user
        try:
            permissions = json.loads(current_user.role.permissions or "[]") if current_user.role else []
        except Exception:
            permissions = []
        if permission not in permissions and "*" not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无操作权限")
        return current_user
    return checker
