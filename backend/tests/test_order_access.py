import pytest
from unittest.mock import Mock

from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant
from app.routes.inventory import reduce_stock


@pytest.fixture
def guest_order(db_session):
    customer = Customer(name="Invitada", email="guest@example.com")
    product = Product(name="Remera", price=2, stock=4, is_unique=False)
    db_session.add_all([customer, product])
    db_session.flush()
    variant = ProductVariant(product_id=product.id, size="M", color="Negro", stock=4)
    db_session.add(variant)
    db_session.flush()
    order = Order(customer_id=customer.id, total=2, payment_method="mercadopago", payment_status="pending_payment", delivery_method="retiro_local")
    db_session.add(order)
    db_session.flush()
    db_session.add(OrderItem(order_id=order.id, product_id=product.id, variant_id=variant.id, price=2, quantity=1))
    reduce_stock(product.id, 1, db_session, variant_id=variant.id)
    db_session.commit()
    return order, variant


def test_guest_access_is_bound_to_one_order(client, guest_order, monkeypatch):
    import hashlib
    import hmac
    order, _ = guest_order
    monkeypatch.setattr(settings, "SECRET_KEY", "test-order-key-with-at-least-32-characters")
    token = hmac.new(settings.SECRET_KEY.encode(), f"order-access:v1:{order.id}".encode(), hashlib.sha256).hexdigest()
    for route in [f"/api/v1/orders/{order.id}", f"/api/v1/payments/status/{order.id}"]:
        assert client.get(route, params={"access_token": token}).status_code == 200
        assert client.get(route, params={"access_token": "invalid"}).status_code == 403
        other_token = hmac.new(settings.SECRET_KEY.encode(), f"order-access:v1:{order.id + 1}".encode(), hashlib.sha256).hexdigest()
        assert client.get(route, params={"access_token": other_token}).status_code == 403
        assert client.get(route).status_code in (401, 403)


def test_return_url_contains_order_token(monkeypatch):
    from app.controllers.payments_controller import _build_return_url
    monkeypatch.setattr(settings, "SECRET_KEY", "test-order-key-with-at-least-32-characters")
    assert "access_token=" in _build_return_url(9)


def test_periodic_reconciliation_approves_without_reducing_stock_again(db_session, guest_order, monkeypatch):
    from app.controllers.payments_controller import payments_controller
    from app.services.order_expiration import run_pending_order_maintenance
    order, variant = guest_order
    fake = Mock(is_configured=True)
    fake.get_charge.return_value = {"status": "approved", "paymentId": "mp-real-test"}
    monkeypatch.setattr(payments_controller, "client", fake)
    monkeypatch.setattr("app.services.notificaciones.notificaciones_service.notificar_pago_confirmado", Mock())
    run_pending_order_maintenance(db_session)
    run_pending_order_maintenance(db_session)
    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "approved"
    assert variant.stock == 3
    fake.get_charge.assert_called_once_with(order.id)


def test_reconciliation_skips_when_another_worker_holds_lock(db_session, monkeypatch):
    from app.controllers.payments_controller import payments_controller
    from app.services.order_expiration import run_pending_order_maintenance
    reconcile = Mock()
    monkeypatch.setattr(payments_controller, "reconcile_pending_payments", reconcile)
    monkeypatch.setattr("app.services.order_expiration._try_acquire_advisory_lock", lambda session: False)
    assert run_pending_order_maintenance(db_session) == []
    reconcile.assert_not_called()


def test_authenticated_owner_and_other_user(client, guest_order, monkeypatch):
    order, _ = guest_order
    verify = Mock(return_value={"uid": "guest-account", "email": "guest@example.com"})
    monkeypatch.setattr("app.core.order_access.verify_firebase_token", verify)
    headers = {"Authorization": "Bearer session-token"}
    assert client.get(f"/api/v1/orders/{order.id}", headers=headers).status_code == 200
    verify.return_value = {"uid": "someone-else", "email": "other@example.com"}
    assert client.get(f"/api/v1/orders/{order.id}", headers=headers).status_code == 403
    assert client.get(f"/api/v1/payments/status/{order.id}", headers=headers).status_code == 403
