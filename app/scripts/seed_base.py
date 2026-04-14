from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.site_settings import SiteSettings
from app.models.user import User
from app.models.user_role import UserRole


BASE_ROLES = ("super_admin", "admin")


def _ensure_roles(db) -> tuple[dict[str, Role], list[str]]:
    existing_roles = db.execute(select(Role)).scalars().all()
    by_name = {role.name: role for role in existing_roles}
    created: list[str] = []

    for role_name in BASE_ROLES:
        if role_name not in by_name:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
            by_name[role_name] = role
            created.append(role_name)

    return by_name, created


def _upsert_site_settings(db, site_name: str) -> str:
    row = db.get(SiteSettings, 1)
    if row is None:
        db.add(SiteSettings(id=1, site_name=site_name))
        return "created"

    if row.site_name != site_name:
        row.site_name = site_name
        return "updated"

    return "unchanged"


def _ensure_super_admin_user(db, email: str, password: str) -> tuple[User, str]:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        user = User(email=email, password_hash=hash_password(password), is_active=True)
        db.add(user)
        db.flush()
        return user, "created"

    if not user.is_active:
        user.is_active = True
        return user, "reactivated"

    return user, "existing"


def _ensure_user_role(db, user_id, role_id: int) -> str:
    link = db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
    ).scalar_one_or_none()

    if link is None:
        db.add(UserRole(user_id=user_id, role_id=role_id))
        return "assigned"

    return "existing"


def main() -> None:
    settings = get_settings()

    if settings.initial_superadmin_password == "change-me-now":
        raise ValueError(
            "INITIAL_SUPERADMIN_PASSWORD is still the default placeholder. "
            "Set a real password in your environment before seeding."
        )

    with SessionLocal() as db:
        roles_by_name, created_roles = _ensure_roles(db)
        site_settings_status = _upsert_site_settings(db, settings.site_name)
        super_admin_user, super_admin_status = _ensure_super_admin_user(
            db,
            settings.initial_superadmin_email,
            settings.initial_superadmin_password,
        )
        super_admin_role_status = _ensure_user_role(
            db,
            super_admin_user.id,
            roles_by_name["super_admin"].id,
        )

        db.commit()

    print("Seed complete.")
    print(
        "roles:",
        f"created={created_roles}" if created_roles else "no changes",
    )
    print(f"site_settings: {site_settings_status}")
    print(f"super_admin_user: {super_admin_status} ({settings.initial_superadmin_email})")
    print(f"super_admin_role: {super_admin_role_status}")


if __name__ == "__main__":
    main()
