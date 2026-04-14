from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SiteSettingsRead(BaseModel):
    id: int
    site_name: str
    customer_name: str | None = None
    logo_url: str | None = None
    support_email: str | None = None
    timezone: str
    theme_json: dict
    updated_at: datetime


class SiteSettingsUpdate(BaseModel):
    site_name: str | None = None
    customer_name: str | None = None
    logo_url: str | None = None
    support_email: str | None = None
    timezone: str | None = None
    theme_json: dict | None = None


class RoleRead(BaseModel):
    id: int
    name: str


class AdminUserRead(BaseModel):
    id: UUID
    email: str
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime


class AdminUserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    is_active: bool = True
    roles: list[str] = Field(default_factory=lambda: ["admin"])


class AdminUserStatusUpdate(BaseModel):
    is_active: bool


class AdminUserRolesUpdate(BaseModel):
    roles: list[str]
