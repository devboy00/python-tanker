from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import get_db
from app.models.role import Role
from app.models.site_settings import SiteSettings
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.admin import (
    AdminUserCreate,
    AdminUserRead,
    AdminUserRolesUpdate,
    AdminUserStatusUpdate,
    RoleRead,
    SiteSettingsRead,
    SiteSettingsUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_super_admin)])


def _roles_by_user_id(db: Session, user_ids: list[UUID]) -> dict[UUID, list[str]]:
    if not user_ids:
        return {}

    rows = db.execute(
        select(UserRole.user_id, Role.name)
        .join(Role, Role.id == UserRole.role_id)
        .where(UserRole.user_id.in_(user_ids))
    ).all()

    by_user: dict[UUID, list[str]] = {user_id: [] for user_id in user_ids}
    for user_id, role_name in rows:
        by_user[user_id].append(role_name)

    for role_names in by_user.values():
        role_names.sort()

    return by_user


def _serialize_user(user: User, roles: list[str]) -> AdminUserRead:
    return AdminUserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=roles,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get(
    "/site-settings",
    response_model=SiteSettingsRead,
)
def get_site_settings(db: Session = Depends(get_db)) -> SiteSettings:
    row = db.get(SiteSettings, 1)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site settings not found.")
    return row


@router.put(
    "/site-settings",
    response_model=SiteSettingsRead,
)
def upsert_site_settings(payload: SiteSettingsUpdate, db: Session = Depends(get_db)) -> SiteSettings:
    settings = get_settings()
    row = db.get(SiteSettings, 1)
    if row is None:
        row = SiteSettings(
            id=1,
            site_name=payload.site_name or settings.site_name,
            customer_name=payload.customer_name,
            logo_url=payload.logo_url,
            support_email=payload.support_email,
            timezone=payload.timezone or "UTC",
            theme_json=payload.theme_json or {},
        )
        db.add(row)
    else:
        data = payload.model_dump(exclude_unset=True)
        for field_name, value in data.items():
            setattr(row, field_name, value)

    db.commit()
    db.refresh(row)
    return row


@router.get(
    "/roles",
    response_model=list[RoleRead],
)
def list_roles(db: Session = Depends(get_db)) -> list[Role]:
    return db.execute(select(Role).order_by(Role.name)).scalars().all()


@router.get(
    "/users",
    response_model=list[AdminUserRead],
)
def list_users(db: Session = Depends(get_db)) -> list[AdminUserRead]:
    users = db.execute(select(User).order_by(User.created_at, User.email)).scalars().all()
    role_map = _roles_by_user_id(db, [user.id for user in users])
    return [_serialize_user(user, role_map.get(user.id, [])) for user in users]


@router.post(
    "/users",
    response_model=AdminUserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db)) -> AdminUserRead:
    email = payload.email.strip().lower()
    if db.execute(select(User).where(User.email == email)).scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    requested_roles = sorted(set(payload.roles or ["admin"]))
    roles = db.execute(select(Role).where(Role.name.in_(requested_roles))).scalars().all()
    found_names = {role.name for role in roles}
    missing_roles = [name for name in requested_roles if name not in found_names]
    if missing_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown roles: {', '.join(missing_roles)}",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        is_active=payload.is_active,
    )
    db.add(user)
    db.flush()

    for role in roles:
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return _serialize_user(user, sorted(found_names))


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserRead,
)
def update_user_status(
    user_id: UUID, payload: AdminUserStatusUpdate, db: Session = Depends(get_db)
) -> AdminUserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    role_map = _roles_by_user_id(db, [user.id])
    return _serialize_user(user, role_map.get(user.id, []))


@router.put(
    "/users/{user_id}/roles",
    response_model=AdminUserRead,
)
def replace_user_roles(
    user_id: UUID, payload: AdminUserRolesUpdate, db: Session = Depends(get_db)
) -> AdminUserRead:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    requested_roles = sorted(set(payload.roles))
    roles = db.execute(select(Role).where(Role.name.in_(requested_roles))).scalars().all()
    found_names = {role.name for role in roles}
    missing_roles = [name for name in requested_roles if name not in found_names]
    if missing_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown roles: {', '.join(missing_roles)}",
        )

    existing_links = db.execute(select(UserRole).where(UserRole.user_id == user.id)).scalars().all()
    for link in existing_links:
        db.delete(link)

    for role in roles:
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return _serialize_user(user, sorted(found_names))
