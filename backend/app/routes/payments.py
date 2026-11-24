from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.controllers.payments_controller import payments_controller
from app.core.security import (
    check_order_ownership_or_admin,
    get_current_user,
    require_admin,
)
from app.db.session import get_session
from app.models.order import Order
from app.core.order_access import get_accessible_order

router = APIRouter()


@router.post("/payments/create-preference")
def create_payment_preference(
    order_id: int,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
) -> Dict[str, Any]:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    check_order_ownership_or_admin(order, user, session)
    return payments_controller.create_preference(order_id, session)


@router.get("/payments/status/{order_id}")
def get_payment_status(
    order_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    order: Order = Depends(get_accessible_order),
) -> Dict[str, Any]:
    return payments_controller.get_payment_status(
        order_id, session, background_tasks=background_tasks
    )


@router.get("/payments/admin/connection-status")
def get_payalert_connection_status(
    user=Depends(require_admin()),
) -> Dict[str, Any]:
    return payments_controller.get_connection_status()


@router.post("/payments/admin/reconcile")
def reconcile_pending_payments(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    user=Depends(require_admin()),
) -> Dict[str, int]:
    return payments_controller.reconcile_pending_payments(
        session, background_tasks=background_tasks
    )
