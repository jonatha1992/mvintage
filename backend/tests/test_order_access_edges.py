from unittest.mock import Mock

import pytest

from app.controllers.payments_controller import payments_controller
from app.models.order import Order
from tests.test_order_access import guest_order


@pytest.mark.parametrize("token", ["inválido", "🔑", "", "bad-token"])
def test_malformed_guest_token_is_forbidden(client, guest_order, token):
    order, _ = guest_order
    response = client.get(f"/api/v1/orders/{order.id}", params={"access_token": token})
    assert response.status_code == 403


def test_reconciliation_pages_without_starving_later_orders(db_session, guest_order, monkeypatch):
    first, _ = guest_order
    for _ in range(101):
        db_session.add(Order(customer_id=first.customer_id, total=2, payment_method="mercadopago",
                             payment_status="pending_payment", delivery_method="retiro_local"))
    db_session.commit()
    sync = Mock(return_value="pending_payment")
    monkeypatch.setattr(payments_controller, "sync_order_payment", sync)
    summary = payments_controller.reconcile_pending_payments(db_session)
    assert summary["checked"] == 102
    assert summary["still_pending"] == 102
    assert sync.call_count == 102
    assert len({call.args[0].id for call in sync.call_args_list}) == 102
