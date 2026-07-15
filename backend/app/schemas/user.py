from datetime import datetime
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str
    description: str | None = None
    permissions: str = "[]"


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: str | None = None


class RoleResponse(RoleBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    real_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role_id: int | None = None
    status: int = 1


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    real_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role_id: int | None = None
    status: int | None = None
    password: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class UserResponse(UserBase):
    id: int
    role_name: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
