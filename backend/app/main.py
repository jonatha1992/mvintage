from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.admin_images import router as admin_images_router
from app.routes.products import router as products_router
from app.routes.customers import router as customers_router
from app.routes.orders import router as orders_router
from app.routes.inventory import router as inventory_router
from app.routes.order_items import router as order_items_router
from app.routes.users import router as users_router
from app.routes.roles import router as roles_router
from app.routes.master_data import router as master_data_router
from app.routes.payments import router as payments_router
from app.routes.admin_payments import router as admin_payments_router
from app.routes.admin_shipping import router as admin_shipping_router
from app.routes.email_verification import router as email_verification_router
from app.routes.shipping_quotes import router as shipping_quotes_router
from app.routes.contact import router as contact_router

# Email functionality moved to /routes/ (standard approach)
from app.core.config import settings
import os
import re
import subprocess
from pathlib import Path
from app.db.migrations import run_migrations
import app.models  # noqa: F401
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tienda Ropa API",
    description="API para sistema de inventario y tienda online",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Ejecutar migraciones automáticamente al iniciar la aplicación."""
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Ejecutar migraciones automáticamente
    try:
        run_migrations()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        # En development podemos continuar, en otros entornos es más crítico
        if settings.ENVIRONMENT not in ["development", "dev"]:
            raise


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Use dynamic origins from settings
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Disposition", "Set-Cookie"],  # Expose additional headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


app.include_router(admin_images_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(order_items_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
app.include_router(master_data_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(admin_payments_router, prefix="/api/v1/orders", tags=["admin"])
app.include_router(admin_shipping_router, prefix="/api/v1")
app.include_router(email_verification_router, prefix="/api/v1")
app.include_router(contact_router, prefix="/api/v1")
app.include_router(shipping_quotes_router, prefix="/api/v1")
# Email functionality moved to standard /routes/

uploads_dir = Path(os.environ.get("UPLOADS_DIR", "/app/uploads"))
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version.json")
def version_json():
    root = Path(__file__).resolve().parents[2]
    version = os.environ.get("APP_VERSION", "1.0.0")
    for candidate in (root / "VERSION", root / "pyproject.toml"):
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8")
            match = re.search(r"(?m)^version\s*=\s*[\"']([^\"']+)", text) if candidate.suffix == ".toml" else re.search(r"\S+", text)
            if match:
                version = match.group(1)
                break
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        version = "1.0.0"
    sha = os.environ.get("GIT_SHA", "")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
        try:
            sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            sha = "unknown"
    return {"version": version, "sha": sha[:7]}
