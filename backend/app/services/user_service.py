from datetime import datetime

from sqlalchemy.orm import Session
from app.models.user import LoginLog, OperationLog, Role, User
from app.schemas.user import RoleCreate, RoleUpdate, UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password


class UserService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 20):
        return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        user = User(**data.model_dump(exclude={"password"}), password=get_password_hash(data.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user: User, data: UserUpdate) -> User:
        values = data.model_dump(exclude_unset=True)
        password = values.pop("password", None)
        for key, value in values.items():
            setattr(user, key, value)
        if password:
            user.password = get_password_hash(password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_login_log(db: Session, username: str, user_id: int | None, success: bool, ip: str = "", user_agent: str = ""):
        db.add(LoginLog(user_id=user_id, username=username, login_status=1 if success else 0, login_ip=ip, user_agent=user_agent))
        db.commit()

    @staticmethod
    def create_operation_log(db: Session, user_id: int | None, op_type: str, module: str, desc: str, ip: str = ""):
        db.add(OperationLog(user_id=user_id, operation_type=op_type, operation_module=module, operation_desc=desc, operation_ip=ip))
        db.commit()


class RoleService:
    @staticmethod
    def list_roles(db: Session):
        return db.query(Role).order_by(Role.id).all()

    @staticmethod
    def get_role(db: Session, role_id: int):
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str):
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def create_role(db: Session, data: RoleCreate) -> Role:
        role = Role(**data.model_dump())
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def update_role(db: Session, role: Role, data: RoleUpdate) -> Role:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(role, key, value)
        db.commit()
        db.refresh(role)
        return role
