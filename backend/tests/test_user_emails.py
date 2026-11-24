import json
from typing import Any, Dict, List, Optional

import httpx
from sqlmodel import Session, select

from app.controllers.user_controller import (
    send_verification_email_async,
    send_welcome_email_async,
)
from app.core.config import settings
from app.models.email_verification import EmailVerificationToken
from app.models.user import User
from app.services.notificaciones import CorreoCentralClient, CorreoCentralError


class FakeUserCorreoClient:
    def __init__(self, *, configured: bool = True, fail: bool = False):
        self._configured = configured
        self.fail = fail
        self.sent: List[Dict[str, Any]] = []

    @property
    def is_configured(self) -> bool:
        return self._configured

    def send_bienvenida(self, **kwargs: Any) -> Optional[str]:
        if not self._configured:
            return None
        if self.fail:
            raise CorreoCentralError("Simulated failure", status_code=502)
        self.sent.append({"template": "bienvenida", **kwargs})
        return f"fake-welcome-{len(self.sent)}"

    def send_codigo(self, **kwargs: Any) -> Optional[str]:
        if not self._configured:
            return None
        if self.fail:
            raise CorreoCentralError("Simulated failure", status_code=502)
        self.sent.append({"template": "codigo", **kwargs})
        return f"fake-code-{len(self.sent)}"


def test_correo_central_client_send_bienvenida_contract():
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.read().decode("utf-8"))
        return httpx.Response(200, json={"id": "msg_welcome_1", "status": "sent"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = CorreoCentralClient(
            base_url="https://correo.tecnofusion.dev",
            api_key="cc_test_key",
            http_client=http_client,
        )
        msg_id = client.send_bienvenida(
            to="cliente@example.com",
            subject="¡Bienvenido!",
            nombre="Ana",
            mensaje="Cuenta creada",
            boton={"texto": "Ir", "url": "https://showroomisabella-ar.web.app"},
            idempotency_key="welcome-1",
        )

    assert msg_id == "msg_welcome_1"
    assert captured["url"] == "https://correo.tecnofusion.dev/v1/send"
    assert captured["auth"] == "Bearer cc_test_key"
    assert captured["body"] == {
        "to": "cliente@example.com",
        "subject": "¡Bienvenido!",
        "idempotencyKey": "welcome-1",
        "template": {
            "id": "bienvenida",
            "data": {
                "nombre": "Ana",
                "mensaje": "Cuenta creada",
                "boton": {"texto": "Ir", "url": "https://showroomisabella-ar.web.app"},
            },
        },
    }


def test_correo_central_client_send_codigo_contract():
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.read().decode("utf-8"))
        return httpx.Response(202, json={"id": "msg_code_1", "status": "queued"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = CorreoCentralClient(
            base_url="https://correo.tecnofusion.dev",
            api_key="cc_test_key",
            http_client=http_client,
        )
        msg_id = client.send_codigo(
            to="cliente@example.com",
            subject="Verificá tu email",
            codigo="123456",
            vencimiento="24 horas",
            titulo="Verificá tu email",
            mensaje="Ingresá el código",
            idempotency_key="verify-1",
        )

    assert msg_id == "msg_code_1"
    assert captured["body"] == {
        "to": "cliente@example.com",
        "subject": "Verificá tu email",
        "idempotencyKey": "verify-1",
        "template": {
            "id": "codigo",
            "data": {
                "codigo": "123456",
                "vencimiento": "24 horas",
                "titulo": "Verificá tu email",
                "mensaje": "Ingresá el código",
            },
        },
    }


def test_send_welcome_email_async_uses_bienvenida_template(monkeypatch):
    monkeypatch.setattr(settings, "STORE_PUBLIC_URL", "https://showroomisabella-ar.web.app")
    fake = FakeUserCorreoClient()

    send_welcome_email_async("ana@example.com", "Ana Pérez", client=fake)

    assert len(fake.sent) == 1
    sent = fake.sent[0]
    assert sent["template"] == "bienvenida"
    assert sent["to"] == "ana@example.com"
    assert sent["nombre"] == "Ana Pérez"
    assert sent["boton"]["url"] == "https://showroomisabella-ar.web.app"


def test_send_welcome_email_async_handles_correo_error():
    fake = FakeUserCorreoClient(fail=True)
    send_welcome_email_async("ana@example.com", "Ana", client=fake)
    assert fake.sent == []


def test_send_verification_email_async_uses_codigo_template(db_session: Session):
    user = User(email="verify@example.com", username="verify", nombre="Lucía")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None

    old_token = EmailVerificationToken.generate_verification_token(
        user_id=user.id, email=user.email
    )
    db_session.add(old_token)
    db_session.commit()

    fake = FakeUserCorreoClient()
    send_verification_email_async(user.id, user.email, "Lucía", client=fake, db=db_session)

    assert len(fake.sent) == 1
    sent = fake.sent[0]
    assert sent["template"] == "codigo"
    assert sent["to"] == "verify@example.com"
    assert sent["vencimiento"] == "24 horas"
    assert len(sent["codigo"]) == 6
    assert "/verify-email?token=" in sent["mensaje"]

    tokens = db_session.exec(
        select(EmailVerificationToken).where(EmailVerificationToken.email == user.email)
    ).all()
    assert len(tokens) == 2
    active = [t for t in tokens if t.used_at is None]
    assert len(active) == 1
    assert active[0].code == sent["codigo"]
