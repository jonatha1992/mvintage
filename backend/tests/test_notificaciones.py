import logging
from typing import Any, Dict, List, Optional

import httpx
import pytest
from sqlmodel import Session

from app.controllers.payments_controller import payments_controller
from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant
from app.services.notificaciones import (
    CorreoCentralClient,
    CorreoCentralError,
    NotificacionesService,
    OrderItemSnapshot,
    OrderNotificationSnapshot,
    format_ars,
    notificaciones_service,
)


class FakeCorreoClient:
    def __init__(self, *, configured: bool = True, fail: bool = False):
        self._configured = configured
        self.fail = fail
        self.sent: List[Dict[str, Any]] = []

    @property
    def is_configured(self) -> bool:
        return self._configured

    def send_aviso(
        self,
        *,
        to: str,
        subject: str,
        titulo: str,
        mensaje: str,
        idempotency_key: str,
        boton: Optional[Dict[str, str]] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        if not self._configured:
            return None
        if self.fail:
            raise CorreoCentralError("Simulated failure", status_code=503)
        self.sent.append(
            {
                "to": to,
                "subject": subject,
                "titulo": titulo,
                "mensaje": mensaje,
                "idempotency_key": idempotency_key,
                "boton": boton,
                "reply_to": reply_to,
            }
        )
        return f"fake-msg-{len(self.sent)}"


class FakePayAlertApproved:
    is_configured = True

    def get_charge(self, order_id: int) -> Dict[str, Any]:
        return {"status": "approved", "paymentId": f"mp-{order_id}"}


@pytest.fixture
def fake_correo(monkeypatch):
    fake = FakeCorreoClient(configured=True)
    monkeypatch.setattr(notificaciones_service, "client", fake)
    return fake


def test_format_ars():
    assert format_ars(28500) == "$28.500"
    assert format_ars(28500.0) == "$28.500"
    assert format_ars(28500.5) == "$28.500,50"
    assert format_ars(1250000) == "$1.250.000"
    assert format_ars(0) == "$0"


def test_correo_central_client_without_key_logs_warning(caplog, monkeypatch):
    monkeypatch.setattr(settings, "CORREO_CENTRAL_API_KEY", "")
    client = CorreoCentralClient(base_url="https://correo.tecnofusion.dev", api_key="")
    assert client.is_configured is False

    with caplog.at_level(logging.WARNING):
        msg_id = client.send_aviso(
            to="cliente@example.com",
            subject="Test",
            titulo="Test",
            mensaje="Hola",
            idempotency_key="test-no-key",
        )
    assert msg_id is None
    assert "CORREO_CENTRAL_API_KEY" in caplog.text


def test_correo_central_client_sends_expected_contract():
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"id": "re_123", "status": "sent"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        client = CorreoCentralClient(
            base_url="https://correo.tecnofusion.dev",
            api_key="cc_test_key",
            http_client=http_client,
        )
        msg_id = client.send_aviso(
            to="cliente@example.com",
            subject="Recibimos tu pedido #10",
            titulo="Recibimos tu pedido #10",
            mensaje="Detalle",
            idempotency_key="showroomisabella-order-10-created-client",
            boton={"texto": "Pedir datos", "url": "https://wa.me/5491176372876?text=Hola"},
        )

    assert msg_id == "re_123"
    assert captured["url"] == "https://correo.tecnofusion.dev/v1/send"
    assert captured["auth"] == "Bearer cc_test_key"
    assert '"id":"aviso"' in captured["body"] or '"id": "aviso"' in captured["body"]
    assert "showroomisabella-order-10-created-client" in captured["body"]


def test_notificar_pedido_creado_transferencia_con_prendas():
    fake = FakeCorreoClient(configured=True)
    service = NotificacionesService(
        client=fake,
        owner_email="Showroomisabella@gmail.com",
        site_url="https://showroomisabella-ar.web.app",
        whatsapp_number="5491176372876",
    )
    snapshot = OrderNotificationSnapshot(
        order_id=42,
        total=28500.0,
        payment_method="transfer",
        customer_name="Sofía Pérez",
        customer_email="sofia@example.com",
        customer_phone="1155667788",
        items=(
            OrderItemSnapshot(
                product_name="Vestido Lino",
                quantity=1,
                price=28500.0,
                color="Crudo",
                talle="M",
            ),
        ),
    )

    service.notificar_pedido_creado(snapshot)

    assert len(fake.sent) == 2
    client_mail, owner_mail = fake.sent

    assert client_mail["to"] == "sofia@example.com"
    assert client_mail["titulo"] == "Recibimos tu pedido #42"
    assert "Vestido Lino" in client_mail["mensaje"]
    assert "Color: Crudo" in client_mail["mensaje"]
    assert "Talle: M" in client_mail["mensaje"]
    assert "$28.500" in client_mail["mensaje"]
    assert "Transferencia bancaria" in client_mail["mensaje"]
    assert "Retiro en el local" in client_mail["mensaje"]
    assert "Alonso Pareja 6542, González Catán (Buenos Aires)" in client_mail["mensaje"]
    assert "coordiná el horario por whatsapp" in client_mail["mensaje"].lower()
    assert "al alias SHOWROOMISABELLAA, a nombre de Priscila Moyano" in client_mail["mensaje"]
    assert "Estado: Esperando tu transferencia" in client_mail["mensaje"]
    assert "3. Te confirmamos el pago por mail" in client_mail["mensaje"]
    assert "Esperando tu transferencia" in client_mail["subject"]
    assert client_mail["boton"] is not None
    assert client_mail["boton"]["url"].startswith("https://wa.me/5491176372876?text=")
    assert "42" in client_mail["boton"]["url"]

    assert owner_mail["to"] == "Showroomisabella@gmail.com"
    assert owner_mail["titulo"] == "Nuevo pedido #42"
    assert "Sofía Pérez" in owner_mail["mensaje"]
    assert "1155667788" in owner_mail["mensaje"]
    assert "sofia@example.com" in owner_mail["mensaje"]
    assert "Vestido Lino" in owner_mail["mensaje"]
    assert "$28.500" in owner_mail["mensaje"]
    assert "Transferencia bancaria" in owner_mail["mensaje"]


def test_post_orders_does_not_send_email_and_notify_created_sends_with_items_idempotently(
    client, db_session: Session, auth_cookie, fake_correo
):
    customer = Customer(
        name="Lucía Gómez",
        email="lucia@example.com",
        phone="1144332211",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    product = Product(name="Vestido Lino", price=28500.0, is_unique=False, stock=0)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    variant = ProductVariant(product_id=product.id, color="Crudo", talle="M", stock=4)
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)

    resp_transfer = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 28500.0,
            "payment_method": "bank_transfer",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )
    assert resp_transfer.status_code == 200
    order_id = resp_transfer.json()["order"]["id"]
    assert len(fake_correo.sent) == 0

    item_resp = client.post(
        "/api/v1/order-items/",
        json={
            "order_id": order_id,
            "product_id": product.id,
            "variant_id": variant.id,
            "quantity": 1,
            "price": 28500.0,
        },
        headers=auth_cookie,
    )
    assert item_resp.status_code == 200
    assert len(fake_correo.sent) == 0

    notify_resp = client.post(
        f"/api/v1/orders/{order_id}/notify-created",
        headers=auth_cookie,
    )
    assert notify_resp.status_code == 200
    assert notify_resp.json() == {
        "order_id": order_id,
        "notified": True,
        "already_notified": False,
    }

    assert len(fake_correo.sent) == 2
    assert fake_correo.sent[0]["to"] == "lucia@example.com"
    assert f"Recibimos tu pedido #{order_id}" == fake_correo.sent[0]["titulo"]
    assert "Vestido Lino" in fake_correo.sent[0]["mensaje"]
    assert "Color: Crudo" in fake_correo.sent[0]["mensaje"]
    assert "Talle: M" in fake_correo.sent[0]["mensaje"]
    assert "$28.500" in fake_correo.sent[0]["mensaje"]
    assert "al alias SHOWROOMISABELLAA, a nombre de Priscila Moyano" in fake_correo.sent[0]["mensaje"]
    assert fake_correo.sent[1]["to"] == "Showroomisabella@gmail.com"
    assert f"Nuevo pedido #{order_id}" == fake_correo.sent[1]["titulo"]
    assert "Vestido Lino" in fake_correo.sent[1]["mensaje"]

    # Segunda llamada es idempotente y no reenvía
    notify_resp_2 = client.post(
        f"/api/v1/orders/{order_id}/notify-created",
        headers=auth_cookie,
    )
    assert notify_resp_2.status_code == 200
    assert notify_resp_2.json() == {
        "order_id": order_id,
        "notified": False,
        "already_notified": True,
    }
    assert len(fake_correo.sent) == 2

    # Pedido Mercado Pago: POST /orders/ no envía, notify-created sí envía
    fake_correo.sent.clear()
    resp_mp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 19900.0,
            "payment_method": "mercadopago",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )
    assert resp_mp.status_code == 200
    mp_order_id = resp_mp.json()["order"]["id"]
    assert len(fake_correo.sent) == 0

    notify_mp = client.post(
        f"/api/v1/orders/{mp_order_id}/notify-created",
        headers=auth_cookie,
    )
    assert notify_mp.status_code == 200
    assert len(fake_correo.sent) == 2
    assert fake_correo.sent[0]["to"] == "lucia@example.com"
    assert f"Recibimos tu pedido #{mp_order_id}" == fake_correo.sent[0]["titulo"]
    assert "Mercado Pago" in fake_correo.sent[0]["mensaje"]
    assert "$19.900" in fake_correo.sent[0]["mensaje"]
    assert "transferí al alias SHOWROOMISABELLAA" not in fake_correo.sent[0]["mensaje"]
    assert fake_correo.sent[1]["to"] == "Showroomisabella@gmail.com"


def test_notify_created_requires_owner_or_admin(
    client, db_session: Session, fake_correo
):
    from app.core.auth_firebase import verify_firebase_token
    from app.main import app

    customer = Customer(name="María López", email="maria@example.com", phone="1133445566")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    order = Order(
        customer_id=customer.id,
        total=18000.0,
        payment_method="transfer",
        delivery_method="retiro_local",
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Otro usuario no admin -> 403
    app.dependency_overrides[verify_firebase_token] = lambda: {
        "uid": "other_uid",
        "email": "intruso@example.com",
        "email_verified": True,
    }
    try:
        resp_forbidden = client.post(f"/api/v1/orders/{order.id}/notify-created")
        assert resp_forbidden.status_code == 403
        assert len(fake_correo.sent) == 0

        # Dueño del pedido (no admin) -> 200
        app.dependency_overrides[verify_firebase_token] = lambda: {
            "uid": "owner_uid",
            "email": "maria@example.com",
            "email_verified": True,
        }
        resp_owner = client.post(f"/api/v1/orders/{order.id}/notify-created")
        assert resp_owner.status_code == 200
        assert resp_owner.json()["notified"] is True
        assert len(fake_correo.sent) == 2
    finally:
        app.dependency_overrides.pop(verify_firebase_token, None)


def test_correo_failure_does_not_break_notify_created(
    client, db_session: Session, auth_cookie, monkeypatch, caplog
):
    failing_client = FakeCorreoClient(configured=True, fail=True)
    monkeypatch.setattr(notificaciones_service, "client", failing_client)

    customer = Customer(name="Ana Ruiz", email="ana@example.com", phone="1199887766")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 15000.0,
            "payment_method": "bank_transfer",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )
    assert resp.status_code == 200
    order_id = resp.json()["order"]["id"]

    with caplog.at_level(logging.ERROR):
        notify_resp = client.post(
            f"/api/v1/orders/{order_id}/notify-created",
            headers=auth_cookie,
        )

    assert notify_resp.status_code == 200
    assert notify_resp.json()["notified"] is True
    assert "Error enviando correo" in caplog.text


def test_payment_confirmed_and_ready_for_pickup_notifications(
    client, db_session: Session, auth_cookie, fake_correo, monkeypatch
):
    monkeypatch.setattr(payments_controller, "client", FakePayAlertApproved())

    customer = Customer(name="Clara Díaz", email="clara@example.com", phone="1122334455")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    product = Product(name="Blusa Seda", price=22000.0, is_unique=False, stock=0)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    variant = ProductVariant(product_id=product.id, color="Negro", talle="S", stock=5)
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)

    # 1. Confirmación por PayAlert (GET /payments/status/{id})
    mp_order = Order(
        customer_id=customer.id,
        total=22000.0,
        payment_method="mercadopago",
        payment_status="pending_payment",
        delivery_method="retiro_local",
    )
    db_session.add(mp_order)
    db_session.commit()
    db_session.refresh(mp_order)

    db_session.add(
        OrderItem(
            order_id=mp_order.id,
            product_id=product.id,
            variant_id=variant.id,
            quantity=1,
            price=22000.0,
        )
    )
    db_session.commit()

    status_resp = client.get(f"/api/v1/payments/status/{mp_order.id}", headers=auth_cookie)
    assert status_resp.status_code == 200
    assert status_resp.json()["payment_status"] == "approved"
    assert len(fake_correo.sent) == 1
    assert fake_correo.sent[0]["to"] == "clara@example.com"
    assert f"#{mp_order.id}" in fake_correo.sent[0]["titulo"]
    assert "Blusa Seda" in fake_correo.sent[0]["mensaje"]
    assert "Color: Negro" in fake_correo.sent[0]["mensaje"]
    assert "Talle: S" in fake_correo.sent[0]["mensaje"]

    # Re-consultar estado ya aprobado no duplica el envío
    fake_correo.sent.clear()
    status_resp_2 = client.get(f"/api/v1/payments/status/{mp_order.id}", headers=auth_cookie)
    assert status_resp_2.status_code == 200
    assert len(fake_correo.sent) == 0

    # 2. Marcar pagado desde admin (PUT /orders/{id}/status)
    transfer_order = Order(
        customer_id=customer.id,
        total=22000.0,
        payment_method="transfer",
        payment_status="pending",
        delivery_method="retiro_local",
    )
    db_session.add(transfer_order)
    db_session.commit()
    db_session.refresh(transfer_order)

    paid_resp = client.put(
        f"/api/v1/orders/{transfer_order.id}/status",
        json={"status": "paid"},
        headers=auth_cookie,
    )
    assert paid_resp.status_code == 200
    assert len(fake_correo.sent) == 1
    assert fake_correo.sent[0]["to"] == "clara@example.com"
    assert f"#{transfer_order.id}" in fake_correo.sent[0]["titulo"]

    # 3. Pasar a Listo para retirar (PUT /orders/{id}/shipping-status)
    fake_correo.sent.clear()
    ready_resp = client.put(
        f"/api/v1/orders/{transfer_order.id}/shipping-status",
        json={"shipping_status": "ready_for_pickup"},
        headers=auth_cookie,
    )
    assert ready_resp.status_code == 200
    assert len(fake_correo.sent) == 1
    assert fake_correo.sent[0]["to"] == "clara@example.com"
    assert "listo para retirar" in fake_correo.sent[0]["titulo"].lower()
    assert "Alonso Pareja 6542, González Catán (Buenos Aires)" in fake_correo.sent[0]["mensaje"]
    assert "coordiná el horario por whatsapp" in fake_correo.sent[0]["mensaje"].lower()
    assert fake_correo.sent[0]["boton"]["url"].startswith("https://wa.me/5491176372876?text=")
