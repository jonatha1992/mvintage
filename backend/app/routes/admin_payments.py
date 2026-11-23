"""
Rutas de administración para gestión de pagos y entregas.
Incluye endpoints para verificar transferencias, programar entregas
y obtener estadísticas del panel admin.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from app.db.session import get_session
from app.core.security import get_current_user, require_admin
from app.models.order import Order
from app.models.customer import Customer
from app.controllers.transfer_controller import transfer_controller
from app.controllers.cash_controller import cash_controller
from app.services.notificaciones import build_order_snapshot, notificaciones_service

router = APIRouter()


def get_current_admin_user(user=Depends(require_admin())):
    """
    Dependencia para verificar que el usuario tiene permisos de administrador.
    Solo usuarios con rol ADMIN pueden acceder a estas rutas.
    """
    return user


@router.get("/admin/filtered")
def get_admin_orders(
    payment_method: Optional[str] = Query(None, description="Filtrar por método de pago"),
    payment_status: Optional[str] = Query(None, description="Filtrar por estado de pago"),
    verification_required: Optional[bool] = Query(None, description="Filtrar por verificación requerida"),
    delivery_status: Optional[str] = Query(None, description="Filtrar por estado de entrega"),
    limit: int = Query(50, description="Cantidad máxima de órdenes"),
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Lista órdenes para panel admin con filtros avanzados.
    Incluye datos del customer y configuración para cada método de pago.
    """
    try:
        query = select(Order)
        
        # Aplicar filtros
        if payment_method and payment_method != "all":
            query = query.where(Order.payment_method == payment_method)
        
        if payment_status and payment_status != "all":
            query = query.where(Order.payment_status == payment_status)
        
        if verification_required is not None:
            query = query.where(Order.verification_required == verification_required)
        
        if delivery_status and delivery_status != "all":
            query = query.where(Order.delivery_status == delivery_status)
        
        # Ordenar por fecha de creación (más recientes primero) y limitar
        orders = session.exec(
            query.order_by(Order.created_at.desc()).limit(limit)
        ).all()
        
        # Enriquecer con datos del customer
        for order in orders:
            order.customer = session.get(Customer, order.customer_id)
        
        return orders
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo órdenes: {str(e)}"
        )


@router.post("/admin/verify-transfer/{order_id}")
def admin_verify_transfer(
    order_id: int,
    verified: bool,
    background_tasks: BackgroundTasks,
    notes: str = "",
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Verificación manual de transferencia bancaria por parte del administrador.
    """
    try:
        existing = session.get(Order, order_id)
        prev_payment_status = existing.payment_status if existing else None
        updated_order = transfer_controller.verify_transfer(order_id, verified, notes, session)
        if verified and prev_payment_status not in ("paid", "approved"):
            snapshot = build_order_snapshot(updated_order, session)
            background_tasks.add_task(notificaciones_service.notificar_pago_confirmado, snapshot)
        
        return {
            "status": "success",
            "order_id": order_id,
            "verified": verified,
            "payment_status": updated_order.payment_status,
            "message": f"Transferencia {'aprobada' if verified else 'rechazada'} exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando transferencia: {str(e)}"
        )


@router.post("/admin/schedule-delivery/{order_id}")
def admin_schedule_delivery(
    order_id: int,
    scheduled_date: datetime,
    time_slot: str,
    notes: str = "",
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Programar entrega para pago en efectivo.
    """
    try:
        # Validar time_slot
        valid_slots = ["mañana", "tarde", "noche"]
        if time_slot not in valid_slots:
            raise HTTPException(
                status_code=400,
                detail=f"time_slot debe ser uno de: {', '.join(valid_slots)}"
            )
        
        updated_order = cash_controller.schedule_delivery(order_id, scheduled_date, time_slot, notes, session)
        
        return {
            "status": "success",
            "order_id": order_id,
            "scheduled_date": scheduled_date.isoformat(),
            "time_slot": time_slot,
            "delivery_status": updated_order.delivery_status,
            "message": "Entrega programada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error programando entrega: {str(e)}"
        )


@router.post("/admin/mark-delivered/{order_id}")
def admin_mark_delivered(
    order_id: int,
    delivery_notes: str = "",
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Marcar una orden como entregada (para pagos en efectivo).
    """
    try:
        updated_order = cash_controller.mark_as_delivered(order_id, delivery_notes, session)
        
        return {
            "status": "success",
            "order_id": order_id,
            "delivery_status": updated_order.delivery_status,
            "payment_status": updated_order.payment_status,
            "message": "Orden marcada como entregada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error marcando como entregada: {str(e)}"
        )


@router.put("/admin/order/{order_id}/notes")
def update_admin_notes(
    order_id: int,
    notes: str,
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Agregar o actualizar notas de administrador en una orden.
    """
    try:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        # Agregar timestamp a las notas
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        new_note = f"[{timestamp}] {notes}"
        
        if order.admin_notes:
            order.admin_notes += f"\n{new_note}"
        else:
            order.admin_notes = new_note
        
        session.add(order)
        session.commit()
        session.refresh(order)
        
        return {
            "status": "success",
            "order_id": order_id,
            "admin_notes": order.admin_notes,
            "message": "Notas actualizadas exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando notas: {str(e)}"
        )


@router.get("/admin/stats")
def get_payment_stats(
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Estadísticas para dashboard de administración.
    """
    try:
        # Órdenes que requieren verificación manual
        pending_verification = session.exec(
            select(func.count(Order.id)).where(
                Order.verification_required == True,
                Order.verified_by_admin.is_(None)
            )
        ).first() or 0
        
        # Entregas pendientes de programación
        pending_delivery = session.exec(
            select(func.count(Order.id)).where(
                Order.delivery_status == "pending"
            )
        ).first() or 0
        
        # Entregas programadas
        scheduled_delivery = session.exec(
            select(func.count(Order.id)).where(
                Order.delivery_status == "scheduled"
            )
        ).first() or 0
        
        # Total pendiente de pago
        total_pending = session.exec(
            select(func.sum(Order.total)).where(
                Order.payment_status.in_(["pending", "pending_payment"])
            )
        ).first() or 0
        
        # Órdenes por método de pago (últimos 30 días)
        orders_by_method = {}
        for method in ["mercadopago", "transfer", "cash"]:
            count = session.exec(
                select(func.count(Order.id)).where(
                    Order.payment_method == method,
                    Order.created_at >= datetime.now().replace(day=1)  # Este mes
                )
            ).first() or 0
            orders_by_method[method] = count
        
        return {
            "pending_verification": pending_verification,
            "pending_delivery": pending_delivery,
            "scheduled_delivery": scheduled_delivery,
            "total_pending_amount": float(total_pending),
            "orders_by_method": orders_by_method,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get("/admin/pending-transfers")
def get_pending_transfers(
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Obtiene lista de transferencias pendientes de verificación.
    """
    try:
        pending_transfers = transfer_controller.get_pending_transfers(session)
        return {
            "transfers": pending_transfers,
            "count": len(pending_transfers)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo transferencias pendientes: {str(e)}"
        )


@router.get("/admin/pending-deliveries")
def get_pending_deliveries(
    session: Session = Depends(get_session),
    user=Depends(get_current_admin_user)
):
    """
    Obtiene lista de entregas pendientes de programación.
    """
    try:
        pending_deliveries = cash_controller.get_pending_deliveries(session)
        return {
            "deliveries": pending_deliveries,
            "count": len(pending_deliveries)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo entregas pendientes: {str(e)}"
        )