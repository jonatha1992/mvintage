import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.routes.inventory import release_order_stock_once
from app.services.notificaciones import build_order_snapshot, notificaciones_service
from app.services.payalert_client import (
    PayAlertClient,
    PayAlertError,
    PayAlertNotConfiguredError,
)
from app.services.payment_installments import order_max_installments

logger = logging.getLogger(__name__)

MAX_CHARGE_AMOUNT_ARS = 1_000_000
PAYMENT_TTL_MINUTES = 15


def _parse_iso_utc(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        return None


def _is_order_expired(order: Order, now: Optional[datetime] = None) -> bool:
    current = now or datetime.utcnow()
    deadline = order.payment_expires_at
    if deadline is None:
        created = order.created_at or current
        deadline = created + timedelta(minutes=PAYMENT_TTL_MINUTES)
    return current >= deadline


def _build_return_url(order_id: int) -> str:
    base = (settings.PAYMENT_RETURN_URL or f"{settings.FRONTEND_URL.rstrip('/')}/payment/return").strip()
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}order_id={order_id}"


class PaymentsController:
    def __init__(self, client: Optional[PayAlertClient] = None):
        self.client = client or PayAlertClient()

    def _recalculate_order_total(self, order: Order, session: Session) -> tuple[float, List[Product]]:
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()
        if not order_items:
            raise HTTPException(status_code=400, detail="La orden no tiene ítems para cobrar")

        total = round(sum(float(item.price) * item.quantity for item in order_items), 2)
        products: List[Product] = []
        for item in order_items:
            product = session.get(Product, item.product_id)
            if product is not None:
                products.append(product)

        if total <= 0:
            raise HTTPException(status_code=400, detail="El total de la orden debe ser mayor a 0")

        if order.total != total:
            order.total = total
            session.add(order)

        return total, products

    def create_preference(self, order_id: int, session: Session) -> Dict[str, Any]:
        if not self.client.is_configured:
            raise HTTPException(status_code=503, detail="Mercado Pago no habilitado")

        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        if order.payment_status in ("approved", "paid"):
            raise HTTPException(status_code=400, detail="La orden ya fue pagada")
        if order.payment_status in ("cancelled", "expired", "needs_refund"):
            raise HTTPException(status_code=400, detail="La orden está cancelada o vencida")

        customer = session.get(Customer, order.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        real_total, products = self._recalculate_order_total(order, session)
        amount = int(round(real_total))
        if amount < 1 or amount > MAX_CHARGE_AMOUNT_ARS:
            raise HTTPException(
                status_code=400,
                detail=f"El monto debe estar entre $1 y ${MAX_CHARGE_AMOUNT_ARS:,} ARS",
            )

        max_installments = order_max_installments(products)
        payer_ref = (customer.email or f"customer-{customer.id}").strip()
        return_url = _build_return_url(order.id)

        try:
            charge = self.client.create_charge(
                order_id=order.id,
                amount=amount,
                payer_ref=payer_ref,
                return_url=return_url,
                payer_email=customer.email or None,
                max_installments=max_installments,
            )
        except PayAlertNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail="Mercado Pago no habilitado") from exc
        except PayAlertError as exc:
            logger.error(f"Error creando cobro en PayAlert para orden {order.id}: {exc}")
            if exc.code == "connection_unavailable":
                raise HTTPException(status_code=503, detail="Mercado Pago no está conectado") from exc
            if exc.status_code == 400:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            if exc.status_code == 409:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            raise HTTPException(status_code=502, detail="Error al crear el cobro en Mercado Pago") from exc

        checkout_url = charge.get("checkoutUrl")
        if not checkout_url:
            raise HTTPException(status_code=502, detail="PayAlert no devolvió checkoutUrl")

        charge_id = charge.get("chargeId")
        expires_at = _parse_iso_utc(charge.get("expiresAt")) or (
            datetime.utcnow() + timedelta(minutes=PAYMENT_TTL_MINUTES)
        )

        order.payment_method = "mercadopago"
        order.payment_status = "pending_payment"
        if charge_id:
            order.mercadopago_preference_id = str(charge_id)
        order.mercadopago_checkout_url = str(checkout_url)
        order.payment_expires_at = expires_at
        session.add(order)
        session.commit()
        session.refresh(order)

        return {
            "charge_id": order.mercadopago_preference_id,
            "preference_id": order.mercadopago_preference_id,
            "checkout_url": order.mercadopago_checkout_url,
            "checkoutUrl": order.mercadopago_checkout_url,
            "init_point": order.mercadopago_checkout_url,
            "expires_at": order.payment_expires_at.isoformat() if order.payment_expires_at else None,
            "status": order.payment_status,
            "order_id": order.id,
            "amount": amount,
        }

    def sync_order_payment(
        self,
        order: Order,
        session: Session,
        now: Optional[datetime] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> str:
        if order.payment_status in ("approved", "paid"):
            return order.payment_status

        if order.payment_method != "mercadopago":
            return order.payment_status

        charge: Optional[Dict[str, Any]] = None
        charge_not_found = False

        if self.client.is_configured and order.id is not None:
            try:
                charge = self.client.get_charge(order.id)
            except PayAlertError as exc:
                if exc.status_code == 404:
                    charge_not_found = True
                else:
                    raise

        if charge is not None:
            remote_status = str(charge.get("status") or "").lower()
            if charge.get("paymentId"):
                order.mercadopago_payment_id = str(charge["paymentId"])
            if charge.get("expiresAt") and order.payment_expires_at is None:
                order.payment_expires_at = _parse_iso_utc(charge.get("expiresAt"))

            if remote_status == "approved":
                just_approved = order.payment_status not in ("approved", "paid")
                if just_approved:
                    if order.stock_released:
                        logger.warning(
                            f"Orden {order.id} aprobada en PayAlert pero su stock ya había sido liberado"
                        )
                    order.payment_status = "approved"
                session.add(order)
                session.commit()
                session.refresh(order)
                if just_approved:
                    snapshot = build_order_snapshot(order, session)
                    if background_tasks is not None:
                        background_tasks.add_task(notificaciones_service.notificar_pago_confirmado, snapshot)
                    else:
                        notificaciones_service.notificar_pago_confirmado(snapshot)
                return order.payment_status

            if remote_status == "needs_refund":
                released = release_order_stock_once(
                    order, session, new_payment_status="needs_refund", commit=False
                )
                if not released:
                    order.payment_status = "needs_refund"
                    session.add(order)
                session.commit()
                session.refresh(order)
                return order.payment_status

            if remote_status in ("rejected", "cancelled", "expired"):
                released = release_order_stock_once(
                    order, session, new_payment_status=remote_status, commit=False
                )
                if not released:
                    order.payment_status = remote_status
                    session.add(order)
                session.commit()
                session.refresh(order)
                return order.payment_status

        if (
            order.payment_status == "pending_payment"
            and _is_order_expired(order, now=now)
            and (charge is not None or charge_not_found or not self.client.is_configured)
        ):
            released = release_order_stock_once(
                order, session, new_payment_status="expired", commit=False
            )
            if not released:
                order.payment_status = "expired"
                session.add(order)
            session.commit()
            session.refresh(order)

        return order.payment_status

    def get_payment_status(
        self,
        order_id: int,
        session: Session,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Dict[str, Any]:
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        sync_warning: Optional[str] = None
        if order.payment_method == "mercadopago" and order.payment_status == "pending_payment":
            try:
                self.sync_order_payment(order, session, background_tasks=background_tasks)
            except PayAlertError as exc:
                logger.warning(f"No se pudo consultar PayAlert para orden {order.id}: {exc}")
                sync_warning = str(exc)

        result: Dict[str, Any] = {
            "order_id": order.id,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "mercadopago_payment_id": order.mercadopago_payment_id,
            "mercadopago_preference_id": order.mercadopago_preference_id,
            "checkout_url": order.mercadopago_checkout_url,
            "checkoutUrl": order.mercadopago_checkout_url,
            "payment_expires_at": (
                order.payment_expires_at.isoformat() if order.payment_expires_at else None
            ),
            "is_expired": _is_order_expired(order),
            "total": order.total,
        }
        if sync_warning:
            result["sync_warning"] = sync_warning
        return result

    def reconcile_pending_payments(
        self,
        session: Session,
        now: Optional[datetime] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Dict[str, int]:
        pending_orders = session.exec(
            select(Order).where(
                Order.payment_method == "mercadopago",
                Order.payment_status == "pending_payment",
            )
        ).all()

        summary = {
            "checked": len(pending_orders),
            "approved": 0,
            "expired": 0,
            "cancelled": 0,
            "rejected": 0,
            "needs_refund": 0,
            "still_pending": 0,
            "errors": 0,
        }

        for order in pending_orders:
            try:
                status = self.sync_order_payment(
                    order, session, now=now, background_tasks=background_tasks
                )
                if status in summary:
                    summary[status] += 1
                else:
                    summary["still_pending"] += 1
            except Exception as exc:
                logger.error(f"Error reconciliando orden {order.id}: {exc}")
                summary["errors"] += 1

        return summary

    def get_connection_status(self) -> Dict[str, Any]:
        if not self.client.is_configured:
            return {
                "configured": False,
                "connected": False,
                "detail": "Mercado Pago no habilitado",
            }
        try:
            data = self.client.get_connection_status()
            return {
                "configured": True,
                "connected": bool(data.get("connected")),
                "deposit_default": data.get("deposit_default"),
            }
        except PayAlertError as exc:
            return {
                "configured": True,
                "connected": False,
                "detail": str(exc),
            }


payments_controller = PaymentsController()
