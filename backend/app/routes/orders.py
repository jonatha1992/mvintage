from typing import List, Optional
import asyncio
from datetime import datetime

import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from app.core.security import (
    get_current_user,
    require_admin,
    is_admin_user,
    check_order_ownership_or_admin,
)
from sqlmodel import Session, select, delete

from app.db.session import get_session
from app.models.order import Order
from app.models.customer import Customer
from app.models.order_item import OrderItem
from app.models.product import Product, ProductImage
from app.controllers.payments_controller import payments_controller
from app.controllers.transfer_controller import transfer_controller
from app.controllers.cash_controller import cash_controller
from app.core.mailer import send_email, render_template
from app.core.config import settings
from app.routes.inventory import reduce_stock, restore_stock

# Configurar logger
logger = logging.getLogger(__name__)
router = APIRouter()


async def send_order_confirmation_email(
    order: Order, customer: Customer, session: Session
):
    """Send order confirmation email asynchronously"""
    try:
        # Get order items with product details
        order_items = session.exec(
            select(OrderItem, Product)
            .where(OrderItem.order_id == order.id)
            .join(Product, OrderItem.product_id == Product.id)
        ).all()

        # Format order items for email
        items_for_email = []
        subtotal = 0
        for order_item, product in order_items:
            item_total = order_item.price * order_item.quantity
            subtotal += item_total
            items_for_email.append(
                {
                    "product_name": product.name,
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                    "total": item_total,
                    "product_image": None,  # Add product image logic if needed
                    "variant_info": None,  # Add variant info if needed
                }
            )

        # Get payment method text
        payment_methods = {
            "transfer": "Transferencia Bancaria",
            "mercadopago": "MercadoPago",
            "cash": "Efectivo Contra Entrega",
        }
        payment_method_text = payment_methods.get(
            order.payment_method, order.payment_method
        )

        # Payment instructions based on method
        payment_instructions = None
        if order.payment_method == "transfer":
            payment_instructions = (
                "Realiza la transferencia e incluye como referencia: ORD-"
                + str(order.id)
            )
        elif order.payment_method == "cash":
            payment_instructions = (
                "Ten el monto exacto disponible al momento de la entrega"
            )

        # Render email template
        html_content = render_template(
            "email_order_confirmation.html",
            app_name=settings.APP_NAME,
            app_url=settings.APP_URL,
            order_number=str(order.id),
            order_date=(
                order.created_at.strftime("%d/%m/%Y %H:%M")
                if order.created_at
                else datetime.now().strftime("%d/%m/%Y %H:%M")
            ),
            customer_name=customer.name,
            order_items=items_for_email,
            subtotal=subtotal,
            discount=0.0,  # Add discount logic if needed
            shipping_cost=0.0,  # Add shipping cost if needed
            total=order.total,
            shipping_address=customer.address,
            shipping_city=customer.city,
            shipping_postal_code=customer.postal_code,
            delivery_notes=customer.delivery_notes,
            payment_method_text=payment_method_text,
            payment_instructions=payment_instructions,
        )

        # Send email
        success = send_email(
            to=customer.email,
            subject=f"Confirmación de pedido #{order.id} - {settings.APP_NAME}",
            html_content=html_content,
        )

        if success:
            print(
                f"✅ Email de confirmación enviado para pedido #{order.id} a {customer.email}"
            )
        else:
            print(f"❌ Error enviando email de confirmación para pedido #{order.id}")

    except Exception as e:
        print(f"❌ Error procesando email de confirmación: {str(e)}")


from pydantic import ValidationError


@router.post("/orders/")
def create_order(
    session: Session = Depends(get_session),
    order: Order = Body(...),
    user=Depends(get_current_user),
):
    # Verificar que el customer existe
    customer = session.get(Customer, order.customer_id)
    if not customer:
        raise HTTPException(status_code=422, detail="Customer not found")

    # Verificar que el customer pertenece al usuario autenticado (a menos que sea admin)
    if not is_admin_user(user, session):
        user_email = (user.get("email") or "").lower()
        if not customer.email or customer.email.lower() != user_email:
            raise HTTPException(
                status_code=403, 
                detail="No tienes permiso para asociar pedidos a este cliente"
            )

    try:
        db_order = Order.model_validate(order)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # Establecer estado inicial según método de pago
    if db_order.payment_method == "mercadopago":
        db_order.payment_status = "pending_payment"
    else:
        db_order.payment_status = "pending"

    # Validar y establecer delivery_method si no viene en el payload
    if not db_order.delivery_method:
        db_order.delivery_method = "envio_andreani"  # default

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    # Manejar según método de pago
    response = {"order": db_order}

    try:
        if db_order.payment_method == "mercadopago":
            # MercadoPago: Crear preferencia automáticamente
            preference_data = payments_controller.create_preference(
                db_order.id, session
            )
            response["payment_preference"] = preference_data

        elif db_order.payment_method == "transfer":
            # Transferencia: Configurar y obtener datos bancarios
            transfer_data = transfer_controller.create_transfer_order(
                db_order.id, session
            )
            response["transfer_info"] = transfer_data

        elif db_order.payment_method == "cash":
            # Efectivo: Calcular entrega y costos
            cash_data = cash_controller.create_cash_order(db_order.id, session)
            response["delivery_info"] = cash_data

    except Exception as e:
        # Si falla la configuración específica, mantener la orden pero informar el error
        response["payment_error"] = str(e)

    # Send order confirmation email asynchronously
    try:
        print(
            f"🔄 Iniciando envío de email de confirmación para orden #{db_order.id} a {customer.email}"
        )
        # Run email sending in background
        import threading

        email_thread = threading.Thread(
            target=lambda: asyncio.run(
                send_order_confirmation_email(db_order, customer, session)
            )
        )
        email_thread.daemon = True  # Ensure thread doesn't prevent app shutdown
        email_thread.start()
        print(f"✅ Thread de email iniciado para orden #{db_order.id}")
    except Exception as e:
        print(f"❌ Error iniciando envío de email para orden #{db_order.id}: {str(e)}")
        # Don't fail the order creation if email fails
        import traceback

        traceback.print_exc()

    return response


@router.get("/orders/", response_model=List[Order])
def read_orders(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    user=Depends(get_current_user),
):
    if is_admin_user(user, session):
        return session.exec(select(Order).offset(skip).limit(limit)).all()

    user_email = (user.get("email") or "").lower()
    if not user_email:
        return []
    customers = session.exec(
        select(Customer).where(Customer.email == user_email)
    ).all()
    if not customers:
        return []
    customer_ids = [c.id for c in customers]
    return session.exec(
        select(Order)
        .where(Order.customer_id.in_(customer_ids))
        .offset(skip)
        .limit(limit)
    ).all()


@router.get("/orders/admin", response_model=List[dict])
def read_orders_with_customer_info(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    user=Depends(require_admin()),
):
    """
    Endpoint para admin que retorna órdenes con información del customer y OrderItems incluida
    """
    try:
        # Force session to see any committed changes
        session.expire_all()

        # Use LEFT JOIN to include orders even if customer is missing
        results = session.exec(
            select(Order, Customer)
            .outerjoin(Customer, Order.customer_id == Customer.id)
            .offset(skip)
            .limit(limit)
            .order_by(Order.created_at.desc())
        ).all()

        # Transform results to include customer info and OrderItems
        orders_with_customer = []
        logger.info(f"📦 Admin endpoint found {len(results)} orders")

        for order, customer in results:
            logger.info(
                f"📋 Order {order.id}: status={order.status}, payment_status={order.payment_status}"
            )
            order_dict = order.model_dump()

            # Handle case where customer might be None
            if customer:
                customer_dict = customer.model_dump()
                # Ensure all address fields are included
                customer_dict.update(
                    {
                        "address": customer.address or "",
                        "city": customer.city or "",
                        "postal_code": customer.postal_code or "",
                        "province": customer.province or "",
                        "country": customer.country or "AR",
                    }
                )
                order_dict["customer"] = customer_dict
            else:
                order_dict["customer"] = {
                    "id": None,
                    "name": "Cliente no encontrado",
                    "email": None,
                    "phone": None,
                    "address": "",
                    "city": "",
                    "postal_code": "",
                    "province": "",
                    "country": "AR",
                }

            # Get order items with product details
            try:
                order_items_query = session.exec(
                    select(OrderItem, Product)
                    .where(OrderItem.order_id == order.id)
                    .join(Product, OrderItem.product_id == Product.id)
                ).all()

                # Format order items
                items_formatted = []
                for order_item, product in order_items_query:
                    item_dict = order_item.model_dump()

                    # Get product with images
                    product_dict = product.model_dump()

                    # Load product images
                    product_images = session.exec(
                        select(ProductImage).where(
                            ProductImage.product_id == product.id
                        )
                    ).all()
                    product_dict["images"] = [
                        img.model_dump() for img in product_images
                    ]

                    item_dict["product"] = product_dict
                    items_formatted.append(item_dict)

                order_dict["items"] = items_formatted

            except Exception as items_error:
                # If items query fails, set empty items list
                print(f"⚠️ Error getting items for order {order.id}: {items_error}")
                order_dict["items"] = []

            # Ensure dates are properly formatted
            if order.created_at:
                order_dict["created_at"] = order.created_at.isoformat()

            # Ensure explicit status fields for frontend clarity
            # Use new shipping_status field, fallback to status for backward compatibility
            try:
                order_dict["shipping_status"] = order.shipping_status or order.status or "pending"
            except Exception:
                order_dict["shipping_status"] = order_dict.get(
                    "shipping_status", order_dict.get("status", "pending")
                )

            try:
                order_dict["payment_status"] = order.payment_status
            except Exception:
                order_dict["payment_status"] = order_dict.get("payment_status", None)

            orders_with_customer.append(order_dict)

        return orders_with_customer

    except Exception as e:
        import logging

        logging.error(f"Error in read_orders_with_customer_info: {e}")
        # Return empty list instead of crashing
        return []


@router.get("/orders/customer/{customer_id}", response_model=List[Order])
def read_customer_orders(
    customer_id: int,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    user=Depends(get_current_user),
):
    """Obtener todos los pedidos de un cliente específico"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if not is_admin_user(user, session):
        user_email = (user.get("email") or "").lower()
        if not customer.email or customer.email.lower() != user_email:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para ver los pedidos de este cliente"
            )

    orders = session.exec(
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return orders


@router.get("/orders/my-orders", response_model=List[dict])
def read_my_orders(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    firebase_user: dict = Depends(get_current_user),
):
    """Obtener todos los pedidos del usuario autenticado con información completa de OrderItems"""
    try:
        # Buscar customers que coincidan con el email del usuario autenticado
        user_email = firebase_user.get("email")
        if not user_email:
            return []  # Si no hay email, retornar lista vacía

        # Encontrar todos los customers con este email usando consulta segura
        customers = session.exec(
            select(Customer).where(Customer.email == user_email)
        ).all()

        if not customers:
            return []  # No hay customers para este usuario, retornar lista vacía

        # Obtener pedidos de todos los customers con este email
        customer_ids = [customer.id for customer in customers]

        # Obtener pedidos
        orders = session.exec(
            select(Order)
            .where(Order.customer_id.in_(customer_ids))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        # Transform orders to include OrderItems with Product info
        orders_formatted = []
        for order in orders:
            try:
                order_dict = order.model_dump()
                if order.created_at:
                    order_dict["created_at"] = order.created_at.isoformat()

                # Get order items with product details
                order_items_query = session.exec(
                    select(OrderItem, Product)
                    .where(OrderItem.order_id == order.id)
                    .join(Product, OrderItem.product_id == Product.id)
                ).all()

                # Format order items
                items_formatted = []
                for order_item, product in order_items_query:
                    item_dict = order_item.model_dump()

                    # Get product with images
                    product_dict = product.model_dump()

                    # Load product images
                    product_images = session.exec(
                        select(ProductImage).where(
                            ProductImage.product_id == product.id
                        )
                    ).all()
                    product_dict["images"] = [
                        img.model_dump() for img in product_images
                    ]

                    item_dict["product"] = product_dict
                    items_formatted.append(item_dict)

                order_dict["items"] = items_formatted
                orders_formatted.append(order_dict)

            except Exception as e:
                # Si un order específico falla, lo saltamos pero continuamos
                print(f"⚠️ Error procesando order {order.id}: {e}")
                continue

        return orders_formatted

    except Exception as e:
        print(f"❌ Error en read_my_orders: {str(e)}")
        import traceback

        traceback.print_exc()
        # Retornar lista vacía en lugar de error 500
        return []


@router.get("/orders/{order_id}", response_model=Order)
def read_order(
    *,
    session: Session = Depends(get_session),
    order_id: int,
    user=Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    check_order_ownership_or_admin(order, user, session)
    return order


@router.put("/orders/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    session: Session = Depends(get_session),
    order: Order = Body(...),
    user=Depends(require_admin()),
):
    db_order = session.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = order.model_dump(exclude_unset=True)
    for key, value in order_data.items():
        setattr(db_order, key, value)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


@router.put("/orders/{order_id}/status")
def update_order_status(
    *,
    session: Session = Depends(get_session),
    order_id: int,
    status_data: dict,
    user=Depends(require_admin()),
):
    """
    Actualizar SOLO el estado de pago de una orden (para admin).
    NO afecta el estado de envío (shipping status).
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update payment status ONLY - do not touch shipping status
    if "status" in status_data:
        new_status = status_data["status"]
        if new_status in ["pending", "paid", "cancelled"]:
            logger.info(
                f"Updating payment_status for order {order.id} from {order.payment_status} to {new_status}"
            )
            order.payment_status = new_status
            # NOTE: We do NOT update order.status here - that's for shipping status only
        else:
            raise HTTPException(status_code=400, detail="Invalid payment status")

    # Update admin notes
    if "adminNotes" in status_data:
        order.admin_notes = status_data["adminNotes"]

    # Set verification info
    order.verified_by_admin = True
    order.admin_verification_date = datetime.utcnow()

    session.add(order)
    session.commit()
    session.refresh(order)

    return {"message": "Order status updated successfully", "order_id": order.id}


@router.put("/orders/{order_id}/shipping-status")
def update_order_shipping_status(
    *,
    session: Session = Depends(get_session),
    order_id: int,
    status_data: dict,
    user=Depends(require_admin()),
):
    """
    Actualizar estado de envío de una orden manualmente (para admin)
    """
    logger.info(f"🔄 Received shipping status update request for order {order_id}")
    logger.info(f"📦 Status data: {status_data}")

    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update shipping status manually
    if "shipping_status" in status_data:
        new_status = status_data["shipping_status"]
        if new_status in [
            "pending",
            "prepared",
            "ready_for_pickup",
            "shipped",
            "delivered",
        ]:
            logger.info(
                f"Manually updating order {order.id} status from {order.status} to {new_status}"
            )
            order.status = new_status

            # If manually set to shipped but no tracking, add timestamp
            if new_status == "shipped" and not order.tracking_number:
                order.shipped_at = datetime.utcnow()
                order.shipped_by = user.id
                logger.info(
                    f"Order {order.id} manually marked as shipped without tracking"
                )
        else:
            raise HTTPException(status_code=400, detail="Invalid shipping status")

    session.add(order)
    session.commit()
    session.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status,
    }


@router.put("/orders/{order_id}/shipping")
def update_order_shipping(
    *,
    session: Session = Depends(get_session),
    order_id: int,
    shipping_data: dict,
    user=Depends(require_admin()),
):
    """
    Actualizar información de envío de una orden (para admin)
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update shipping info
    if "trackingNumber" in shipping_data:
        order.tracking_number = shipping_data["trackingNumber"]

    if "shippingProvider" in shipping_data:
        order.shipping_provider = shipping_data["shippingProvider"]

    if "estimatedDelivery" in shipping_data and shipping_data["estimatedDelivery"]:
        order.estimated_delivery = datetime.fromisoformat(
            shipping_data["estimatedDelivery"]
        )

    if "shippingNotes" in shipping_data:
        order.delivery_notes_shipping = shipping_data["shippingNotes"]

    # Set shipping timestamp and admin who shipped
    order.shipped_at = datetime.utcnow()
    order.shipped_by = user.id
    order.tracking_updated_at = datetime.utcnow()

    # Auto-update order status to shipped when tracking number is provided
    # This means the order has been taken to the shipping provider (correo)
    if "trackingNumber" in shipping_data and shipping_data["trackingNumber"]:
        logger.info(
            f"Adding tracking to order {order.id}. Previous status: {order.status}"
        )
        # Set order status to shipped (means it was taken to the post office)
        order.status = "shipped"
        # Payment status remains unchanged - it's independent from shipping status
        logger.info(
            f"Order {order.id} marked as shipped. Payment status unchanged: {order.payment_status}"
        )
    else:
        # Only add tracking info/notes, don't change status automatically
        # Status changes should be done manually via the /shipping-status endpoint
        logger.info(
            f"Shipping info updated for order {order.id}, shipping_data: {shipping_data}. Status remains: {order.status}"
        )

    session.add(order)
    session.commit()
    session.refresh(order)

    return {"message": "Order shipping updated successfully", "order_id": order.id}


@router.delete("/orders/{order_id}", response_model=dict)
def delete_order(
    *,
    session: Session = Depends(get_session),
    order_id: int,
    user=Depends(require_admin()),
):
    try:
        # Obtener la orden con sus items
        order = session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Obtener los items de la orden antes de eliminarla
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order_id)
        ).all()

        try:
            logger.info(f"Attempting to delete order {order_id}")

            # Restaurar el stock de cada producto
            for item in order_items:
                if not restore_stock(item.product_id, item.quantity, session):
                    logger.warning(
                        f"No se pudo restaurar el stock para el producto {item.product_id}"
                    )

            # Eliminar la orden (los order_items se eliminarán en cascada)
            session.delete(order)
            session.commit()

            logger.info(f"Order {order_id} deleted successfully and stock restored")
            return {
                "status": "success",
                "message": "Order deleted successfully and stock restored",
                "ok": True,
            }

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting order {order_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error deleting order: {str(e)}"
            )

    except HTTPException:
        # Re-lanzar las excepciones HTTP
        raise

    except Exception as e:
        logger.error(f"Unexpected error deleting order {order_id}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while deleting the order",
        )
