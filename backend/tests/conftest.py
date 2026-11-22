"""Fixtures de tests aisladas: nunca conectan con bases configuradas en archivos .env."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

BACKEND_DIR = Path(__file__).resolve().parent.parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

# Debe definirse antes de importar la aplicación: config.py puede cargar archivos .env.
os.environ["ENVIRONMENT"] = "dev"
os.environ["DATABASE_URL"] = "sqlite://"

from app.core.auth_firebase import verify_firebase_token
from app.db.session import get_session
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole

# StaticPool mantiene una única base SQLite en memoria para todas las conexiones del test.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Registra todas las tablas relacionadas antes de create_all.
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def db_session(setup_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_cookie(client, db_session):
    firebase_user = {
        "uid": "test_firebase_uid_api_test",
        "email": "apitest@example.com",
        "name": "API Test User",
        "email_verified": True,
    }

    user = db_session.exec(
        select(User).where(User.firebase_uid == firebase_user["uid"])
    ).first()
    if user is None:
        role = db_session.exec(select(Role).where(Role.name == "admin")).first()
        if role is None:
            role = Role(name="admin", description="Administrator role")
            db_session.add(role)
            db_session.flush()

        user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user["email"],
            username="apitest",
            nombre=firebase_user["name"],
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(UserRole(user_id=user.id, role_id=role.id))
        db_session.commit()

    app.dependency_overrides[verify_firebase_token] = lambda: firebase_user
    yield {"Authorization": "Bearer isolated-test-token"}
    app.dependency_overrides.pop(verify_firebase_token, None)
