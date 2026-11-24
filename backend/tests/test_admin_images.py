from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest

from sqlmodel import select

from app.models.role import Role
from app.models.user_role import UserRole
from app.core.config import settings
from app.controllers.transfer_controller import TransferController

from app.core.security import get_current_db_user
from app.main import app


URL = "/api/v1/admin/images/upload"


def test_upload_rejects_user_without_admin_or_manager_role(client):
    app.dependency_overrides[get_current_db_user] = lambda: SimpleNamespace(id=-1)
    response = client.post(
        URL, data={"folder": "productos"}, files={"file": ("foto.webp", b"image", "image/webp")}
    )
    assert response.status_code == 403


@pytest.mark.parametrize("content_type,size,status", [
    ("text/plain", 5, 422),
    ("image/webp", 15 * 1024 * 1024 + 1, 413),
])
def test_upload_rejects_invalid_file(client, auth_cookie, content_type, size, status):
    with patch("app.routes.admin_images.httpx.Client") as upstream:
        response = client.post(
            URL, headers=auth_cookie, data={"folder": "productos"},
            files={"file": ("foto.webp", b"x" * size, content_type)},
        )
    assert response.status_code == status
    upstream.assert_not_called()


@pytest.mark.parametrize("folder", ["productos", "productos/originals"])
def test_upload_forwards_image_and_returns_public_url(client, auth_cookie, monkeypatch, folder):
    monkeypatch.setattr(settings, "IMG_SERVER_API_KEY", "backend-test-only")
    monkeypatch.setattr(settings, "IMG_SERVER_URL", "https://images.example/")
    public_url = "https://images.example/showroomisabella/image/upload/productos/foto.webp"
    requests = []

    def receive_upload(request):
        requests.append(request)
        assert str(request.url) == "https://images.example/v1/showroomisabella/upload"
        assert request.headers["X-API-Key"] == "backend-test-only"
        assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
        body = request.read()
        assert folder.encode() in body
        assert b'filename="foto.webp"' in body
        assert b"Content-Type: image/webp" in body
        assert b"webp-content" in body
        return httpx.Response(201, json={"secure_url": public_url, "private": "not-exposed"})

    upstream = httpx.Client(transport=httpx.MockTransport(receive_upload))
    with patch("app.routes.admin_images.httpx.Client", return_value=upstream):
        response = client.post(
            URL, headers=auth_cookie, data={"folder": folder},
            files={"file": ("foto.webp", b"webp-content", "image/webp")},
        )
    assert len(requests) == 1
    assert response.status_code == 200
    assert response.json() == {"secure_url": public_url}


@pytest.mark.parametrize("folder", ["../productos", "otra-cuenta", "productos/otra", ""])
def test_upload_rejects_folder_outside_allowlist(client, auth_cookie, folder):
    with patch("app.routes.admin_images.httpx.Client") as upstream:
        response = client.post(
            URL, headers=auth_cookie, data={"folder": folder},
            files={"file": ("foto.webp", b"image", "image/webp")},
        )
    assert response.status_code == 422
    upstream.assert_not_called()


def test_upload_requires_authentication(client):
    response = client.post(
        URL, data={"folder": "productos"}, files={"file": ("foto.webp", b"image", "image/webp")}
    )
    assert response.status_code == 403


def test_upload_without_server_key_returns_503(client, auth_cookie, monkeypatch):
    monkeypatch.setattr(settings, "IMG_SERVER_API_KEY", "")
    response = client.post(
        URL, headers=auth_cookie, data={"folder": "productos"},
        files={"file": ("foto.webp", b"image", "image/webp")},
    )
    assert response.status_code == 503


@pytest.mark.parametrize("result", ["timeout", "unauthorized", "invalid-json", "invalid-url"])
def test_upload_does_not_expose_upstream_errors(client, auth_cookie, monkeypatch, result):
    monkeypatch.setattr(settings, "IMG_SERVER_API_KEY", "backend-test-only")
    with patch("app.routes.admin_images.httpx.Client") as upstream:
        post = upstream.return_value.__enter__.return_value.post
        if result == "timeout":
            post.side_effect = httpx.ReadTimeout("secret-upstream-detail")
        else:
            post.return_value = httpx.Response(
                401 if result == "unauthorized" else 200,
                content=b"secret-upstream-detail" if result == "invalid-json" else b'{"secure_url":"invalid"}',
                request=httpx.Request("POST", "https://images.example"),
            )
        response = client.post(
            URL, headers=auth_cookie, data={"folder": "productos"},
            files={"file": ("foto.webp", b"image", "image/webp")},
        )
    assert response.status_code == 502
    assert response.json() == {"detail": "Error del servidor de imágenes"}


@pytest.mark.parametrize("role_name,status", [("manager", 503), ("employee", 403), ("user", 403)])
def test_upload_checks_assigned_role(client, auth_cookie, db_session, monkeypatch, role_name, status):
    assignment = db_session.exec(select(UserRole)).one()
    role = Role(name=role_name, description=role_name)
    db_session.add(role)
    db_session.flush()
    assignment.role_id = role.id
    db_session.add(assignment)
    db_session.commit()
    monkeypatch.setattr(settings, "IMG_SERVER_API_KEY", "")
    response = client.post(
        URL, headers=auth_cookie, data={"folder": "productos"},
        files={"file": ("foto.webp", b"image", "image/webp")},
    )
    assert response.status_code == status


def test_transfer_bank_defaults(db_session):
    info = TransferController().get_bank_info(db_session)
    assert info["alias"] == "SHOWROOMISABELLAA"
    assert info["holder_name"] == "Priscila Moyano"
