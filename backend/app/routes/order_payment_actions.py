from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.controllers.payments_controller import payments_controller
from app.core.config import settings
from app.core.order_access import get_accessible_order
from app.db.session import get_session
from app.models.order import Order
from app.routes.inventory import release_order_stock_once
from app.services.notificaciones import build_order_snapshot, notificaciones_service

router = APIRouter()


def require_pending_payment(order: Order) -> None:
    if (order.payment_status != "pending_payment" or order.transfer_verified
            or order.verified_by_admin or order.stock_released):
        raise HTTPException(status_code=409, detail="Este pedido ya no permite cambios de pago")


@router.post("/orders/{order_id}/pay-with-mercadopago")
def pay_with_mercadopago(
    order: Order = Depends(get_accessible_order),
    session: Session = Depends(get_session),
):
    session.refresh(order, with_for_update=True)
    require_pending_payment(order)
    if order.created_at + timedelta(hours=settings.PENDING_ORDER_TTL_HOURS) <= datetime.utcnow():
        raise HTTPException(status_code=409, detail="El plazo para pagar este pedido venció")
    if order.payment_method == "mercadopago" and order.mercadopago_checkout_url:
        return {"order_id": order.id, "checkout_url": order.mercadopago_checkout_url}
    if order.payment_method != "bank_transfer":
        raise HTTPException(status_code=409, detail="Solo podés cambiar una transferencia pendiente")
    return payments_controller.create_preference(order.id, session)


@router.post("/orders/{order_id}/cancel")
def cancel_customer_order(
    background_tasks: BackgroundTasks,
    order: Order = Depends(get_accessible_order),
    session: Session = Depends(get_session),
):
    session.refresh(order, with_for_update=True)
    if order.payment_status == "cancelled" and order.stock_released:
        return {"order_id": order.id, "payment_status": "cancelled"}
    require_pending_payment(order)
    if order.payment_method != "bank_transfer":
        raise HTTPException(status_code=409, detail="Solo podés cancelar una transferencia pendiente")
    release_order_stock_once(order, session, new_payment_status="cancelled")
    snapshot = build_order_snapshot(order, session)
    background_tasks.add_task(notificaciones_service.notificar_pedido_cancelado, snapshot)
    return {"order_id": order.id, "payment_status": order.payment_status}
