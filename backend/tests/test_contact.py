from unittest.mock import Mock

import pytest

from app.services.notificaciones import CorreoCentralClient


def test_contact_sends_owner_email(client, monkeypatch):
    send = Mock(return_value="contact-message-id")
    monkeypatch.setattr(CorreoCentralClient, "send_aviso", send)
    monkeypatch.setattr(CorreoCentralClient, "is_configured", property(lambda self: True))
    response = client.post("/api/v1/contact", json={
        "nombre": " Ana ", "email": "ana@example.com", "mensaje": "Quiero consultar por una remera."
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Recibimos tu mensaje. Te responderemos por email."}
    from app.core.config import settings
    assert send.call_args.kwargs["to"] == settings.NOTIFY_OWNER_EMAIL
    assert send.call_args.kwargs["reply_to"] == "ana@example.com"
    assert "ana@example.com" in send.call_args.kwargs["mensaje"]
    assert "Ana" in send.call_args.kwargs["mensaje"]


@pytest.mark.parametrize("values", [
    {},
    {"nombre": " ", "email": "ana@example.com", "mensaje": "Una consulta válida"},
    {"nombre": "Ana", "email": "invalido", "mensaje": "Una consulta válida"},
    {"nombre": "Ana", "email": "ana@example.com", "mensaje": "x" * 4001},
])
def test_contact_rejects_invalid_input(client, values):
    assert client.post("/api/v1/contact", json=values).status_code == 422


def test_contact_rate_limit(client, monkeypatch):
    send = Mock(return_value="contact-id")
    monkeypatch.setattr(CorreoCentralClient, "send_aviso", send)
    monkeypatch.setattr(CorreoCentralClient, "is_configured", property(lambda self: True))
    payload = {"nombre": "Ana", "email": "ana@example.com", "mensaje": "Una consulta válida"}
    for _ in range(3):
        assert client.post("/api/v1/contact", json=payload).status_code == 200
    response = client.post("/api/v1/contact", json=payload)
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert send.call_count == 3


def test_contact_delivery_failure_is_not_success(client, monkeypatch):
    from app.services.notificaciones import CorreoCentralError
    monkeypatch.setattr(CorreoCentralClient, "is_configured", property(lambda self: True))
    monkeypatch.setattr(CorreoCentralClient, "send_aviso", Mock(side_effect=CorreoCentralError("upstream")))
    response = client.post("/api/v1/contact", json={
        "nombre": "Ana", "email": "ana@example.com", "mensaje": "Una consulta válida"
    })
    assert response.status_code == 502
    assert "WhatsApp" in response.json()["detail"]


def test_api_security_headers(client):
    for url in ["/health", "/not-found"]:
        response = client.get(url)
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"

