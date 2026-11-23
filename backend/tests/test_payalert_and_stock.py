from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest
from sqlmodel import Session

from app.controllers.payments_controller import PaymentsController, payments_controller
from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant
from app.routes.inventory import reduce_stock
from app.services.payalert_client import PayAlertError


class FakePayAlertClient:
    def __init__(
        self,
        configured: bool = True,
        charge_response: Optional[Dict[str, Any]] = None,
        status_response: Optional[Dict[str, Any]] = None,
        connection_response: Optional[Dict[str, Any]] = None,
        get_charge_error: Optional[Exception] = None,
    ):
        self.is_configured = configured
        self.charge_response = charge_response or {
            "chargeId": "chg_test_123",
            "checkoutUrl": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=test",
            "expiresAt": (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z",
            "status": "pending",
        }
        self.status_response = status_response or {"status": "pending"}
        self.connection_response = connection_response or {
            "connected": True,
            "deposit_default": None,
        }
        self.get_charge_error = get_charge_error
        self.created_charges: List[Dict[str, Any]] = []
        self.get_charge_calls: int = 0

    def create_charge(self, **kwargs: Any) -> Dict[str, Any]:
        self.created_charges.append(kwargs)
        return self.charge_response

    def get_charge(self, order_id: int) -> Dict[str, Any]:
        self.get_charge_calls += 1
        if self.get_charge_error is not None:
            raise self.get_charge_error
        return self.status_response

    def get_connection_status(self) -> Dict[str, Any]:
        return self.connection_response


def _create_customer(db: Session, email: str = "apitest@example.com") -> Customer:
    c = Customer(name="Cliente Test", email=email, phone="1155551234")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _create_product_with_variant(db: Session, stock: int = 5, price: float = 25000.0):
    p = Product(
        name="Campera Vintage",
        price=price,
        stock=stock,
        is_unique=False,
        max_installments=3,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    v = ProductVariant(product_id=p.id, size="M", color="Negro", stock=stock)
    db.add(v)
    db.commit()
    db.refresh(v)
    return p, v


def test_create_order_item_with_variant_decrements_stock_and_updates_total(
    client, auth_cookie, db_session
):
    customer = _create_customer(db_session)
    product, variant = _create_product_with_variant(db_session, stock=4, price=15000.0)

    order_resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 0,
            "payment_method": "mercadopago",
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
            "product_id": product.id,
            "variant_id": variant.id,
            "quantity": 2,
            "price": 15000.0,
        },
        headers=auth_cookie,
    )
    assert item_resp.status_code == 200, item_resp.text
    assert item_resp.json()["variant_id"] == variant.id

    db_session.refresh(variant)
    assert variant.stock == 2

    order = db_session.get(Order, order_id)
    assert order is not None
    assert order.total == 30000.0


def test_insufficient_variant_stock_rejected(client, auth_cookie, db_session):
    customer = _create_customer(db_session)
    product, variant = _create_product_with_variant(db_session, stock=1, price=10000.0)

    order_resp = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "total": 0,
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
            "product_id": product.id,
            "variant_id": variant.id,
            "quantity": 2,
            "price": 10000.0,
        },
        headers=auth_cookie,
    )
    assert item_resp.status_code == 400
    assert "Stock insuficiente" in item_resp.json()["detail"]

    db_session.refresh(variant)
    assert variant.stock == 1


def test_create_preference_without_api_key_returns_503(
    client, auth_cookie, db_session, monkeypatch
):
    monkeypatch.setattr(settings, "PAYALERT_API_KEY", "")
    original_client = payments_controller.client
    payments_controller.client = FakePayAlertClient(configured=False)
    try:
        customer = _create_customer(db_session)
        product, variant = _create_product_with_variant(db_session, stock=3, price=12000.0)
        order = Order(
            customer_id=customer.id,
            total=12000.0,
            payment_method="mercadopago",
            payment_status="pending_payment",
            delivery_method="retiro_local",
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        db_session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                variant_id=variant.id,
                quantity=1,
                price=12000.0,
            )
        )
        db_session.commit()

        resp = client.post(
            f"/api/v1/payments/create-preference?order_id={order.id}",
            headers=auth_cookie,
        )
        assert resp.status_code == 503
        assert resp.json()["detail"] == "Mercado Pago no habilitado"
    finally:
        payments_controller.client = original_client


def test_create_preference_and_approved_status_idempotent(
    client, auth_cookie, db_session
):
    fake = FakePayAlertClient(
        configured=True,
        status_response={"status": "approved", "paymentId": "mp_pay_999"},
    )
    original_client = payments_controller.client
    payments_controller.client = fake
    try:
        customer = _create_customer(db_session)
        product, variant = _create_product_with_variant(db_session, stock=3, price=20000.0)

        order_resp = client.post(
            "/api/v1/orders/",
            json={
                "customer_id": customer.id,
                "total": 0,
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
                "product_id": product.id,
                "variant_id": variant.id,
                "quantity": 2,
                "price": 20000.0,
            },
            headers=auth_cookie,
        )
        assert item_resp.status_code == 200

        pref_resp = client.post(
            f"/api/v1/payments/create-preference?order_id={order_id}",
            headers=auth_cookie,
        )
        assert pref_resp.status_code == 200, pref_resp.text
        body = pref_resp.json()
        assert body["checkoutUrl"] == fake.charge_response["checkoutUrl"]
        assert fake.created_charges[0]["amount"] == 40000
        assert fake.created_charges[0]["order_id"] == order_id

        status1 = client.get(f"/api/v1/payments/status/{order_id}", headers=auth_cookie)
        assert status1.status_code == 200
        assert status1.json()["payment_status"] == "approved"
        assert status1.json()["mercadopago_payment_id"] == "mp_pay_999"
        assert fake.get_charge_calls == 1

        # Segunda consulta debe ser idempotente sin volver a consultar PayAlert
        status2 = client.get(f"/api/v1/payments/status/{order_id}", headers=auth_cookie)
        assert status2.status_code == 200
        assert status2.json()["payment_status"] == "approved"
        assert fake.get_charge_calls == 1
    finally:
        payments_controller.client = original_client


def test_expired_order_releases_variant_stock_once(db_session):
    fake = FakePayAlertClient(
        configured=True,
        status_response={"status": "pending"},
    )
    controller = PaymentsController(client=fake)
    customer = _create_customer(db_session)
    product, variant = _create_product_with_variant(db_session, stock=3, price=18000.0)

    assert reduce_stock(product.id, 2, db_session, variant_id=variant.id) is True
    db_session.refresh(variant)
    assert variant.stock == 1

    order = Order(
        customer_id=customer.id,
        total=36000.0,
        payment_method="mercadopago",
        payment_status="pending_payment",
        delivery_method="retiro_local",
        created_at=datetime.utcnow() - timedelta(minutes=20),
        payment_expires_at=datetime.utcnow() - timedelta(minutes=5),
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    db_session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            variant_id=variant.id,
            quantity=2,
            price=18000.0,
        )
    )
    db_session.commit()

    summary1 = controller.reconcile_pending_payments(db_session)
    assert summary1["checked"] == 1
    assert summary1["expired"] == 1

    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "expired"
    assert order.stock_released is True
    assert variant.stock == 3

    # Volver a reconciliar o sincronizar no debe restaurar stock por segunda vez
    controller.sync_order_payment(order, db_session)
    summary2 = controller.reconcile_pending_payments(db_session)
    assert summary2["checked"] == 0
    db_session.refresh(variant)
    assert variant.stock == 3


def test_public_webhook_removed(client):
    resp = client.post("/api/v1/payments/webhook", json={"type": "payment"})
    assert resp.status_code == 404


def test_concurrent_last_unit_purchase_only_one_succeeds(tmp_path):
    from sqlmodel import SQLModel, create_engine

    db_file = tmp_path / "race.db"
    race_engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False, "timeout": 15},
    )
    SQLModel.metadata.create_all(race_engine)

    with Session(race_engine) as seed_session:
        p = Product(name="Prenda Única Variante", price=10000.0, stock=1, is_unique=False)
        seed_session.add(p)
        seed_session.commit()
        seed_session.refresh(p)
        v = ProductVariant(product_id=p.id, size="S", color="Rojo", stock=1)
        seed_session.add(v)
        seed_session.commit()
        seed_session.refresh(v)
        product_id = p.id
        variant_id = v.id

    def attempt_buy(_: int) -> bool:
        with Session(race_engine) as s:
            return reduce_stock(product_id, 1, s, variant_id=variant_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt_buy, [1, 2]))

    assert results.count(True) == 1
    assert results.count(False) == 1

    with Session(race_engine) as check_session:
        final_variant = check_session.get(ProductVariant, variant_id)
        assert final_variant is not None
        assert final_variant.stock == 0
