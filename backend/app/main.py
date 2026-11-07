from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Email functionality moved to /routes/ (standard approach)
from app.core.config import settings
from fastapi import Depends
import os
import re
import subprocess
from pathlib import Path
from app.db.session import get_session
from app.db.migrations import run_migrations
from sqlmodel import Session, select
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.product import Product, ProductImage, ProductVariant
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventory import Inventory
from app.models.email_verification import EmailVerificationToken
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
app.include_router(shipping_quotes_router, prefix="/api/v1")
# Email functionality moved to standard /routes/


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


@app.get("/debug/auth")
def debug_auth():
    """Endpoint para debuggear la configuración de Firebase"""
    import firebase_admin

    try:
        app_instance = firebase_admin.get_app()
        return {
            "status": "Firebase initialized",
            "app_name": app_instance.name,
            "project_id": app_instance.project_id,
        }
    except ValueError:
        return {"status": "Firebase not initialized", "error": "No app instance found"}
    except Exception as e:
        return {"status": "Firebase error", "error": str(e)}


@app.get("/debug/dump", response_model=None)
def debug_dump(db: Session = Depends(get_session)):
    """Devuelve un volcado compacto de tablas principales (solo para desarrollo)."""

    def rows(model):
        return [r.__dict__ for r in db.exec(select(model)).all()]

    return {
        "environment": settings.ENVIRONMENT,
        "users": rows(User),
        "roles": rows(Role),
        "user_roles": rows(UserRole),
        "products": rows(Product),
        "product_images": rows(ProductImage),
        "product_variants": rows(ProductVariant),
        "customers": rows(Customer),
        "orders": rows(Order),
        "order_items": rows(OrderItem),
        "inventory": rows(Inventory),
    }
