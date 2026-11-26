import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import text, update
from sqlmodel import Session, col, select

from app.core.config import settings
from app.db.session import engine
from app.models.order import Order
from app.models.order_item import OrderItem
from app.routes.inventory import restore_stock

logger = logging.getLogger(__name__)

PENDING_ORDER_TTL_HOURS: int = settings.PENDING_ORDER_TTL_HOURS
PENDING_ORDER_CLEANUP_INTERVAL_MINUTES: int = settings.PENDING_ORDER_CLEANUP_INTERVAL_MINUTES
EXPIRATION_ADVISORY_LOCK_KEY: int = 42081924


def _is_postgresql(session: Session) -> bool:
    bind = session.get_bind()
    return bind is not None and bind.dialect.name == "postgresql"


def _try_acquire_advisory_lock(session: Session) -> bool:
    if not _is_postgresql(session):
        return True
    acquired = session.exec(
        text("SELECT pg_try_advisory_lock(:key)"),
        params={"key": EXPIRATION_ADVISORY_LOCK_KEY},
    ).scalar()
    return bool(acquired)


def _release_advisory_lock(session: Session) -> None:
    if not _is_postgresql(session):
        return
    try:
        session.exec(
            text("SELECT pg_advisory_unlock(:key)"),
            params={"key": EXPIRATION_ADVISORY_LOCK_KEY},
        )
    except Exception as exc:
        logger.warning("No se pudo liberar advisory lock de vencimiento: %s", exc)


def cancel_expired_pending_orders(
    session: Session,
    now: Optional[datetime] = None,
    ttl_hours: Optional[int] = None,
) -> List[int]:
    effective_ttl = PENDING_ORDER_TTL_HOURS if ttl_hours is None else ttl_hours
    cutoff = (now or datetime.utcnow()) - timedelta(hours=effective_ttl)

    if not _try_acquire_advisory_lock(session):
        logger.info("Vencimiento de pedidos omitido: lock tomado por otra réplica")
        return []

    try:
        stmt = (
            update(Order)
            .where(
                col(Order.payment_status) == "pending_payment",
                col(Order.stock_released).is_(False),
                col(Order.created_at).is_not(None),
                col(Order.created_at) <= cutoff,
            )
            .values(
                payment_status="cancelled",
                status="cancelled",
                stock_released=True,
            )
            .returning(Order.id)
        )
        cancelled_ids = [row[0] for row in session.exec(stmt).all()]
        if not cancelled_ids:
            session.commit()
            return []

        items = session.exec(
            select(OrderItem).where(col(OrderItem.order_id).in_(cancelled_ids))
        ).all()
        for item in items:
            restored = restore_stock(
                item.product_id,
                item.quantity,
                session,
                variant_id=item.variant_id,
                commit=False,
            )
            if not restored:
                logger.warning(
                    "No se pudo restaurar stock para orden #%s (product_id=%s, variant_id=%s, qty=%s)",
                    item.order_id,
                    item.product_id,
                    item.variant_id,
                    item.quantity,
                )

        session.commit()
        logger.info(
            "Pedidos cancelados automáticamente por vencimiento (>%sh): %s",
            effective_ttl,
            cancelled_ids,
        )
        return cancelled_ids
    except Exception:
        session.rollback()
        raise
    finally:
        _release_advisory_lock(session)


def run_pending_order_maintenance(session: Session) -> List[int]:
    from app.controllers.payments_controller import payments_controller

    if not _try_acquire_advisory_lock(session):
        return []
    try:
        payments_controller.reconcile_pending_payments(session)
    except Exception:
        session.rollback()
        raise
    finally:
        _release_advisory_lock(session)
    return cancel_expired_pending_orders(session)


def run_pending_order_expiration_once(custom_engine=None) -> List[int]:
    eng = custom_engine if custom_engine is not None else engine
    # Mantener la misma conexión durante los commits conserva el advisory lock.
    with eng.connect() as connection, Session(bind=connection) as session:
        return run_pending_order_maintenance(session)


async def pending_order_expiration_loop(interval_seconds: Optional[int] = None) -> None:
    sleep_seconds = (
        min(PENDING_ORDER_CLEANUP_INTERVAL_MINUTES, 2) * 60
        if interval_seconds is None
        else interval_seconds
    )
    while True:
        try:
            await asyncio.to_thread(run_pending_order_expiration_once)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Error en tarea periódica de vencimiento de pedidos: %s", exc)
        await asyncio.sleep(sleep_seconds)
