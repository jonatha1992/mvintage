import logging
from datetime import datetime, timedelta

from sqlmodel import Session

from app.controllers.payments_controller import PaymentsController
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant
from app.routes.inventory import reduce_stock
from app.services.order_expiration import (
    PENDING_ORDER_TTL_HOURS,
    cancel_expired_pending_orders,
)


class _LatePaymentClient:
    is_configured = True

    def __init__(self, payment_id: str = "mp_late_777"):
        self.payment_id = payment_id

    def get_charge(self, order_id: int):
        return {"status": "approved", "paymentId": self.payment_id}


def _seed_order(
    db: Session,
    *,
    age_hours: float,
    payment_status: str = "pending_payment",
    payment_method: str = "mercadopago",
    initial_stock: int = 5,
    qty: int = 2,
):
    customer = Customer(name="Ana", email=f"ana-{age_hours}@example.com", phone="1155550000")
    db.add(customer)
    db.commit()
    db.refresh(customer)

    product = Product(name="Remera Isabella", price=15000.0, stock=initial_stock, is_unique=False)
    db.add(product)
    db.commit()
    db.refresh(product)

    variant = ProductVariant(product_id=product.id, size="M", color="Blanco", stock=initial_stock)
    db.add(variant)
    db.commit()
    db.refresh(variant)

    assert reduce_stock(product.id, qty, db, variant_id=variant.id) is True

    order = Order(
        customer_id=customer.id,
        total=15000.0 * qty,
        payment_method=payment_method,
        payment_status=payment_status,
        delivery_method="retiro_local",
        created_at=datetime.utcnow() - timedelta(hours=age_hours),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    db.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            variant_id=variant.id,
            quantity=qty,
            price=15000.0,
        )
    )
    db.commit()
    return order, variant


def test_pending_order_older_than_ttl_cancels_and_restores_variant_stock(db_session):
    order, variant = _seed_order(db_session, age_hours=PENDING_ORDER_TTL_HOURS + 1, initial_stock=5, qty=2)
    db_session.refresh(variant)
    assert variant.stock == 3

    cancelled = cancel_expired_pending_orders(db_session)
    assert cancelled == [order.id]

    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "cancelled"
    assert order.status == "cancelled"
    assert order.stock_released is True
    assert variant.stock == 5


def test_pending_order_within_ttl_is_not_cancelled(db_session):
    order, variant = _seed_order(db_session, age_hours=PENDING_ORDER_TTL_HOURS - 2, initial_stock=5, qty=2)

    cancelled = cancel_expired_pending_orders(db_session)
    assert cancelled == []

    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "pending_payment"
    assert order.stock_released is False
    assert variant.stock == 3


def test_paid_order_older_than_ttl_is_not_cancelled(db_session):
    order, variant = _seed_order(
        db_session,
        age_hours=PENDING_ORDER_TTL_HOURS + 10,
        payment_status="approved",
        initial_stock=5,
        qty=2,
    )

    cancelled = cancel_expired_pending_orders(db_session)
    assert cancelled == []

    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "approved"
    assert order.stock_released is False
    assert variant.stock == 3


def test_expiration_double_run_is_idempotent(db_session):
    order, variant = _seed_order(db_session, age_hours=PENDING_ORDER_TTL_HOURS + 3, initial_stock=4, qty=2)

    first = cancel_expired_pending_orders(db_session)
    second = cancel_expired_pending_orders(db_session)

    assert first == [order.id]
    assert second == []

    db_session.refresh(variant)
    assert variant.stock == 4


def test_late_payment_on_cancelled_order_does_not_reactivate_and_marks_review(db_session, caplog):
    order, variant = _seed_order(db_session, age_hours=PENDING_ORDER_TTL_HOURS + 5, initial_stock=3, qty=1)
    assert cancel_expired_pending_orders(db_session) == [order.id]
    db_session.refresh(order)
    db_session.refresh(variant)
    assert order.payment_status == "cancelled"
    assert variant.stock == 3

    controller = PaymentsController(client=_LatePaymentClient("mp_late_999"))
    with caplog.at_level(logging.WARNING):
        status = controller.sync_order_payment(order, db_session)

    db_session.refresh(order)
    db_session.refresh(variant)
    assert status == "cancelled"
    assert order.payment_status == "cancelled"
    assert order.verification_required is True
    assert order.admin_notes is not None
    assert "mp_late_999" in order.admin_notes
    assert "revisión manual" in order.admin_notes
    assert variant.stock == 3
    assert any("Pago tardío aprobado" in r.message for r in caplog.records)
