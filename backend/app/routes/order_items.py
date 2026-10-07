from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import (
    get_current_user,
    require_admin,
    is_admin_user,
    check_order_ownership_or_admin,
)
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.db.session import get_session
from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.product import Product
from app.routes.inventory import reduce_stock, restore_stock

router = APIRouter()


class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(gt=0)
    price: float = Field(default=0.0, ge=0)


def _recalculate_order_total(order: Order, session: Session):
    """Recalculate order total from actual database order items"""
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()
    calculated_total = sum(item.price * item.quantity for item in items)
    if order.delivery_cost:
        calculated_total += order.delivery_cost
    order.total = calculated_total
    session.add(order)


@router.post("/order-items/", response_model=OrderItem)
def create_order_item(
    *,
    session: Session = Depends(get_session),
    order_item_data: OrderItemCreate = Body(...),
    user=Depends(get_current_user)
):
    if order_item_data.quantity <= 0:
        raise HTTPException(status_code=422, detail="quantity must be greater than 0")
    
    order = session.get(Order, order_item_data.order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_item_data.order_id} not found")

    check_order_ownership_or_admin(order, user, session)

    product = session.get(Product, order_item_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {order_item_data.product_id} not found")

    stock_available = reduce_stock(order_item_data.product_id, order_item_data.quantity, session)
    if not stock_available:
        raise HTTPException(
            status_code=400, 
            detail=f"Stock insuficiente para el producto {order_item_data.product_id}. Cantidad solicitada: {order_item_data.quantity}"
        )
    
    # Usar siempre el precio del producto verificado del backend
    db_order_item = OrderItem(
        order_id=order_item_data.order_id,
        product_id=order_item_data.product_id,
        quantity=order_item_data.quantity,
        price=product.price
    )

    session.add(db_order_item)
    session.commit()
    session.refresh(db_order_item)
    
    _recalculate_order_total(order, session)
    session.commit()

    return db_order_item


@router.get("/order-items/", response_model=List[OrderItem])
def read_order_items(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    user=Depends(require_admin())
):
    order_items = session.exec(select(OrderItem).offset(skip).limit(limit)).all()
    return order_items


@router.get("/order-items/{order_item_id}", response_model=OrderItem)
def read_order_item(
    *,
    session: Session = Depends(get_session),
    order_item_id: int,
    user=Depends(get_current_user)
):
    order_item = session.get(OrderItem, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    order = session.get(Order, order_item.order_id)
    if order:
        check_order_ownership_or_admin(order, user, session)
        
    return order_item


@router.put("/order-items/{order_item_id}", response_model=OrderItem)
def update_order_item(
    *,
    session: Session = Depends(get_session),
    order_item_id: int,
    order_item_data: OrderItemCreate = Body(...),
    user=Depends(require_admin())
):
    db_order_item = session.get(OrderItem, order_item_id)
    if not db_order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    if order_item_data.quantity <= 0:
        raise HTTPException(status_code=422, detail="quantity must be greater than 0")
    
    product = session.get(Product, order_item_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_order_item.order_id = order_item_data.order_id
    db_order_item.product_id = order_item_data.product_id
    db_order_item.quantity = order_item_data.quantity
    db_order_item.price = product.price
    
    session.add(db_order_item)
    session.commit()
    session.refresh(db_order_item)
    
    order = session.get(Order, db_order_item.order_id)
    if order:
        _recalculate_order_total(order, session)
        session.commit()

    return db_order_item


@router.delete("/order-items/{order_item_id}")
def delete_order_item(
    *,
    session: Session = Depends(get_session),
    order_item_id: int,
    user=Depends(require_admin())
):
    order_item = session.get(OrderItem, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    restore_stock(order_item.product_id, order_item.quantity, session)
    order_id = order_item.order_id
    session.delete(order_item)
    session.commit()

    order = session.get(Order, order_id)
    if order:
        _recalculate_order_total(order, session)
        session.commit()

    return {"ok": True}