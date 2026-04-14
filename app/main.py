from fastapi import FastAPI

from app.api.routes import admin_router, auth_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
