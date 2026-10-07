"""
Rutas de pagos con MercadoPago
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.db.session import get_session
from app.core.security import get_current_user, check_order_ownership_or_admin
from app.models.order import Order
from app.controllers.payments_controller import payments_controller

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/payments/create-preference")
def create_payment_preference(
    order_id: int,
    session: Session = Depends(get_session),
    user=Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Crea una preferencia de pago en MercadoPago para una orden específica
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    check_order_ownership_or_admin(order, user, session)
    return payments_controller.create_preference(order_id, session)


@router.post("/payments/webhook")
async def mercadopago_webhook(
    request: Request,
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Webhook para recibir notificaciones de MercadoPago
    No requiere autenticación ya que viene de MercadoPago
    """
    try:
        webhook_data = await request.json()
        result = payments_controller.process_webhook(webhook_data, session)
        if result.get("status") == "error":
            reason = result.get("reason", "unknown_error")
            logger.error(f"MercadoPago webhook error: {reason}")
            if reason in ["missing_payment_id", "missing_external_reference"]:
                raise HTTPException(status_code=400, detail=reason)
            raise HTTPException(status_code=500, detail=reason)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando webhook: {str(e)}")


@router.get("/payments/status/{order_id}")
def get_payment_status(
    order_id: int,
    session: Session = Depends(get_session),
    user=Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene el estado actual de pago de una orden
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    check_order_ownership_or_admin(order, user, session)
    return payments_controller.get_payment_status(order_id, session)
