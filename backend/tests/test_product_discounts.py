from datetime import datetime, timedelta, timezone
from typing import Any, cast

from app.controllers.payments_controller import PaymentsController
from app.controllers.transfer_controller import transfer_controller
from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product


def _product_payload(**overrides):
    payload = {
        "name": "Vestido Promo",
        "description": "Vestido de lino",
        "price": 45000.0,
        "genero": "femenino",
        "estado": "nuevo",
        "categoria": "Vestidos",
        "is_unique": True,
        "color": "NEGRO",
        "talle": "M",
        "stock": 5,
        "images": ["https://img.tecnofusion.dev/productos/vestido.webp"],
        "variants": [],
        "has_discount": False,
        "max_installments": 3,
    }
    payload.update(overrides)
    return payload


def test_effective_price_rounds_to_whole_pesos_and_respects_dates():
    now = datetime(2026, 11, 24, 15, 0, 0)
    product = Product(
        name="Remera",
        price=12345.0,
        is_unique=True,
        stock=2,
        has_discount=True,
        discount_percentage=15,
        promo_label="Liquidación",
    )
    # 12345 * 0.85 = 10493.25 -> 10493
    assert product.is_discount_active(now) is True
    assert product.effective_price(now) == 10493.0
    assert product.active_discount_amount(now) == 1852.0

    # Futuro: todavía no empezó
    product.discount_starts_at = now + timedelta(hours=1)
    assert product.is_discount_active(now) is False
    assert product.effective_price(now) == 12345.0

    # En ventana
    product.discount_starts_at = now - timedelta(hours=1)
    product.discount_ends_at = now + timedelta(hours=1)
    assert product.is_discount_active(now) is True
    assert product.effective_price(now) == 10493.0

    # Vencido
    product.discount_ends_at = now - timedelta(minutes=1)
    assert product.is_discount_active(now) is False
    assert product.effective_price(now) == 12345.0

    # Timezone-aware (UTC-3) normalizado correctamente
    tz_ar = timezone(timedelta(hours=-3))
    product.discount_starts_at = datetime(2026, 11, 24, 11, 0, 0, tzinfo=tz_ar)  # 14:00 UTC
    product.discount_ends_at = datetime(2026, 11, 24, 13, 0, 0, tzinfo=tz_ar)  # 16:00 UTC
    assert product.is_discount_active(now) is True


def test_discount_api_validations_and_serialization(client, auth_cookie):
    # Porcentaje fuera de rango (0 y 91)
    r0 = client.post("/api/v1/products/", json=_product_payload(has_discount=True, discount_percentage=0), headers=auth_cookie)
    assert r0.status_code == 400

    r91 = client.post("/api/v1/products/", json=_product_payload(has_discount=True, discount_percentage=91), headers=auth_cookie)
    assert r91.status_code == 400

    # Sin porcentaje
    r_none = client.post("/api/v1/products/", json=_product_payload(has_discount=True), headers=auth_cookie)
    assert r_none.status_code == 400

    # Etiqueta > 20 caracteres
    r_label = client.post(
        "/api/v1/products/",
        json=_product_payload(has_discount=True, discount_percentage=20, promo_label="X" * 21),
        headers=auth_cookie,
    )
    assert r_label.status_code in (400, 422)

    # Fecha fin < fecha inicio
    now = datetime.utcnow()
    r_dates = client.post(
        "/api/v1/products/",
        json=_product_payload(
            has_discount=True,
            discount_percentage=20,
            discount_starts_at=(now + timedelta(days=2)).isoformat(),
            discount_ends_at=(now + timedelta(days=1)).isoformat(),
        ),
        headers=auth_cookie,
    )
    assert r_dates.status_code == 400

    # Creación válida con descuento activo y etiqueta
    ok = client.post(
        "/api/v1/products/",
        json=_product_payload(
            has_discount=True,
            discount_percentage=20,
            promo_label="  Black Friday  ",
            discount_starts_at=(now - timedelta(hours=1)).isoformat(),
            discount_ends_at=(now + timedelta(days=2)).isoformat(),
        ),
        headers=auth_cookie,
    )
    assert ok.status_code == 200, ok.text
    data = ok.json()
    assert data["has_discount"] is True
    assert data["discount_active"] is True
    assert data["discounted_price"] == 36000.0
    assert data["discount_amount"] == 9000.0
    assert data["promo_label"] == "Black Friday"

    # Desactivar descuento limpia campos al actualizar
    off = client.put(
        f"/api/v1/products/{data['id']}",
        json=_product_payload(has_discount=False),
        headers=auth_cookie,
    )
    assert off.status_code == 200, off.text
    off_data = off.json()
    assert off_data["has_discount"] is False
    assert off_data["discount_active"] is False
    assert off_data["discount_percentage"] is None
    assert off_data["promo_label"] is None
    assert off_data["discount_starts_at"] is None
    assert off_data["discount_ends_at"] is None
    assert off_data["discounted_price"] == 45000.0


def test_order_transfer_and_payalert_use_server_discounted_price(client, auth_cookie, db_session):
    # Producto con 25% OFF sobre $40.000 -> $30.000
    prod_resp = client.post(
        "/api/v1/products/",
        json=_product_payload(price=40000.0, has_discount=True, discount_percentage=25, promo_label="Promo"),
        headers=auth_cookie,
    )
    assert prod_resp.status_code == 200
    prod = prod_resp.json()

    customer = Customer(name="Clienta Promo", email="promo@example.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Frontend intenta mandar total=$1 y precio=$1: el servidor debe ignorarlos
    order_resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 1.0,
            "payment_method": "bank_transfer",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )
    assert order_resp.status_code == 200, order_resp.text
    order_id = order_resp.json()["order"]["id"]

    item_resp = client.post(
        "/api/v1/order-items/",
        json={
            "order_id": order_id,
            "product_id": prod["id"],
            "quantity": 2,
            "price": 1.0,
        },
        headers=auth_cookie,
    )
    assert item_resp.status_code == 200, item_resp.text
    assert item_resp.json()["price"] == 30000.0

    order_in_db = db_session.get(Order, order_id)
    assert order_in_db is not None
    assert order_in_db.total == 60000.0

    # Transferencia recalcula desde los ítems en BD (incluso si order.total fuera alterado)
    order_in_db.total = 99.0
    db_session.add(order_in_db)
    db_session.commit()
    transfer_info = transfer_controller.create_transfer_order(order_id, db_session)
    assert transfer_info["total_amount"] == 60000.0

    # PayAlert / Mercado Pago recalcula desde los ítems y cobra $60.000 entero
    captured = {}

    class FakePayAlertClient:
        is_configured = True

        def create_charge(self, **kwargs):
            captured.update(kwargs)
            return {
                "chargeId": "chg_test_1",
                "checkoutUrl": "https://mp.test/checkout/1",
                "expiresAt": (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z",
            }

    order_in_db.total = 5.0
    order_in_db.payment_status = "pending"
    db_session.add(order_in_db)
    db_session.commit()

    ctrl = PaymentsController(client=cast(Any, FakePayAlertClient()))
    pref = ctrl.create_preference(order_id, db_session)
    assert pref["amount"] == 60000
    assert captured["amount"] == 60000


def test_order_ignores_expired_discount(client, auth_cookie, db_session):
    now = datetime.utcnow()
    prod_resp = client.post(
        "/api/v1/products/",
        json=_product_payload(
            price=20000.0,
            has_discount=True,
            discount_percentage=30,
            discount_starts_at=(now - timedelta(days=5)).isoformat(),
            discount_ends_at=(now - timedelta(days=1)).isoformat(),
        ),
        headers=auth_cookie,
    )
    assert prod_resp.status_code == 200
    prod = prod_resp.json()
    assert prod["discount_active"] is False
    assert prod["discounted_price"] == 20000.0

    customer = Customer(name="Clienta Vencida", email="vencida@example.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    order_resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 14000.0,
            "payment_method": "mercadopago",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )
    order_id = order_resp.json()["order"]["id"]

    item_resp = client.post(
        "/api/v1/order-items/",
        json={
            "order_id": order_id,
            "product_id": prod["id"],
            "quantity": 1,
            "price": 14000.0,
        },
        headers=auth_cookie,
    )
    assert item_resp.status_code == 200
    assert item_resp.json()["price"] == 20000.0
