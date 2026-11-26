from unittest.mock import Mock

import pytest
from app.core.order_access import order_access_token
from tests.test_order_access import guest_order


@pytest.fixture
def transfer_order(guest_order, db_session):
    order, variant = guest_order
    order.payment_method = "bank_transfer"
    db_session.add(order)
    db_session.commit()
    return order, variant


def test_change_transfer_to_mercadopago(client, db_session, transfer_order, monkeypatch):
    from app.controllers.payments_controller import payments_controller
    order, _ = transfer_order
    fake = Mock(is_configured=True)
    fake.create_charge.return_value = {"chargeId": "qa-charge", "checkoutUrl": "https://example.com/pay"}
    monkeypatch.setattr(payments_controller, "client", fake)
    response = client.post(f"/api/v1/orders/{order.id}/pay-with-mercadopago", params={"access_token": order_access_token(order.id)})
    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://example.com/pay"
    db_session.refresh(order)
    assert order.payment_method == "mercadopago"
    assert fake.create_charge.call_args.kwargs["title"] == f"Pedido #{order.id} - Showroom Isabella"


def test_cancel_restores_variant_once_and_notifies_owner(client, db_session, transfer_order, monkeypatch):
    order, variant = transfer_order
    notify = Mock()
    monkeypatch.setattr("app.services.notificaciones.notificaciones_service.notificar_pedido_cancelado", notify)
    for _ in range(2):
        response = client.post(f"/api/v1/orders/{order.id}/cancel", params={"access_token": order_access_token(order.id)})
        assert response.status_code == 200
    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "cancelled"
    assert order.stock_released
    assert variant.stock == 4
    notify.assert_called_once()


@pytest.mark.parametrize("field,value", [("payment_status", "approved"), ("payment_status", "paid"), ("transfer_verified", True), ("verified_by_admin", True)])
@pytest.mark.parametrize("action", ["cancel", "pay-with-mercadopago"])
def test_paid_or_admin_verified_cannot_retract(client, db_session, transfer_order, field, value, action):
    order, variant = transfer_order
    setattr(order, field, value)
    db_session.add(order)
    db_session.commit()
    response = client.post(f"/api/v1/orders/{order.id}/{action}", params={"access_token": order_access_token(order.id)})
    assert response.status_code == 409
    db_session.refresh(variant)
    assert variant.stock == 3


@pytest.mark.parametrize("action", ["cancel", "pay-with-mercadopago"])
def test_other_user_cannot_retract(client, transfer_order, monkeypatch, action):
    order, _ = transfer_order
    monkeypatch.setattr("app.core.order_access.verify_firebase_token", lambda credentials: {"uid": "other", "email": "other@example.com"})
    response = client.post(f"/api/v1/orders/{order.id}/{action}", headers={"Authorization": "Bearer other-user"})
    assert response.status_code == 403
