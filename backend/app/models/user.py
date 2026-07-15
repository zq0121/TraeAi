from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    permissions = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    real_name = Column(String(100))
    email = Column(String(120))
    phone = Column(String(30))
    role_id = Column(Integer, ForeignKey("roles.id"))
    status = Column(Integer, default=1)
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    role = relationship("Role", back_populates="users")
    login_logs = relationship("LoginLog", back_populates="user", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="user", cascade="all, delete-orphan")
    detection_records = relationship("DetectionRecord", back_populates="user")


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100))
    login_time = Column(DateTime, default=datetime.now)
    login_ip = Column(String(50))
    login_status = Column(Integer, default=0)
    user_agent = Column(Text)

    user = relationship("User", back_populates="login_logs")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operation_type = Column(String(50))
    operation_module = Column(String(50))
    operation_desc = Column(Text)
    operation_time = Column(DateTime, default=datetime.now)
    operation_ip = Column(String(50))

    user = relationship("User", back_populates="operation_logs")
