from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from app.core.security import get_current_user
from sqlalchemy import update
from sqlmodel import Session, col, select

from app.db.session import get_session
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant

# Configurar logger
logger = logging.getLogger(__name__)
router = APIRouter()


from pydantic import ValidationError

@router.post("/inventory/", response_model=Inventory)
def create_inventory(session: Session = Depends(get_session), inventory: Inventory = Body(...), user=Depends(get_current_user)):
    # Verificar que el producto existe
    product = session.get(Product, inventory.product_id)
    if not product:
        raise HTTPException(status_code=422, detail="Product not found")
    
    try:
        db_inventory = Inventory.model_validate(inventory)
    except ValidationError as e:
        # Convert validation errors to JSON serializable format
        error_details = []
        for error in e.errors():
            error_dict = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": error.get("input")
            }
            error_details.append(error_dict)
        raise HTTPException(status_code=422, detail=error_details)
        
    session.add(db_inventory)
    session.commit()
    session.refresh(db_inventory)
    return db_inventory


@router.get("/inventory/", response_model=List[Inventory])
def read_inventory(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100, user=Depends(get_current_user)
):
    inventory = session.exec(select(Inventory).offset(skip).limit(limit)).all()
    return inventory


@router.get("/inventory/{inventory_id}", response_model=Inventory)
def read_inventory_item(*, session: Session = Depends(get_session), inventory_id: int, user=Depends(get_current_user)):
    inventory_item = session.get(Inventory, inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item


@router.put("/inventory/{inventory_id}", response_model=Inventory)
def update_inventory(
    inventory_id: int, session: Session = Depends(get_session), inventory: Inventory = Body(...), user=Depends(get_current_user)
):
    db_inventory = session.get(Inventory, inventory_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    inventory_data = inventory.model_dump(exclude_unset=True)
    for key, value in inventory_data.items():
        setattr(db_inventory, key, value)
    session.add(db_inventory)
    session.commit()
    session.refresh(db_inventory)
    return db_inventory


@router.delete("/inventory/{inventory_id}")
def delete_inventory(*, session: Session = Depends(get_session), inventory_id: int, user=Depends(get_current_user)):
    inventory_item = session.get(Inventory, inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    session.delete(inventory_item)
    session.commit()
    return {"ok": True}


def restore_stock(
    product_id: int,
    quantity: int,
    session: Session,
    variant_id: Optional[int] = None,
    commit: bool = True,
) -> bool:
    if quantity <= 0:
        return False
    try:
        if variant_id is not None:
            stmt = (
                update(ProductVariant)
                .where(
                    ProductVariant.id == variant_id,
                    ProductVariant.product_id == product_id,
                )
                .values(stock=ProductVariant.stock + quantity)
            )
            result = session.exec(stmt)
            if result.rowcount != 1:
                logger.error(f"Variante {variant_id} del producto {product_id} no encontrada")
                return False
            if commit:
                session.commit()
            else:
                session.flush()
            variant = session.get(ProductVariant, variant_id)
            if variant is not None:
                session.refresh(variant)
            return True

        product = session.get(Product, product_id)
        if not product:
            logger.error(f"Producto con ID {product_id} no encontrado")
            return False

        if product.stock is not None:
            stmt = (
                update(Product)
                .where(col(Product.id) == product_id)
                .values(stock=col(Product.stock) + quantity)
            )
            session.exec(stmt)
        else:
            product.stock = quantity
            session.add(product)

        if commit:
            session.commit()
        else:
            session.flush()
        session.refresh(product)
        return True
    except Exception as e:
        if commit:
            session.rollback()
        logger.error(f"Error al restaurar stock para producto {product_id}: {str(e)}")
        return False


def reduce_stock(
    product_id: int,
    quantity: int,
    session: Session,
    variant_id: Optional[int] = None,
    commit: bool = True,
) -> bool:
    if quantity <= 0:
        return False
    try:
        product = session.get(Product, product_id)
        if not product:
            return False

        if variant_id is not None:
            stmt = (
                update(ProductVariant)
                .where(
                    ProductVariant.id == variant_id,
                    ProductVariant.product_id == product_id,
                    ProductVariant.stock >= quantity,
                )
                .values(stock=ProductVariant.stock - quantity)
            )
            result = session.exec(stmt)
            if result.rowcount != 1:
                return False
            if commit:
                session.commit()
            else:
                session.flush()
            variant = session.get(ProductVariant, variant_id)
            if variant is not None:
                session.refresh(variant)
            return True

        if product.is_unique:
            stmt = (
                update(Product)
                .where(
                    col(Product.id) == product_id,
                    col(Product.stock).is_not(None),
                    col(Product.stock) >= quantity,
                )
                .values(stock=col(Product.stock) - quantity)
            )
            result = session.exec(stmt)
            if result.rowcount != 1:
                return False
            if commit:
                session.commit()
            else:
                session.flush()
            session.refresh(product)
            return True

        inventory_item = session.exec(
            select(Inventory).where(Inventory.product_id == product_id)
        ).first()

        if not inventory_item:
            if not product.variants:
                return False
            total_variant_stock = sum(variant.stock or 0 for variant in product.variants)
            if total_variant_stock < quantity:
                return False
            inventory_item = Inventory(
                product_id=product_id,
                quantity=total_variant_stock - quantity,
                last_update=datetime.now(),
            )
            session.add(inventory_item)
        else:
            if inventory_item.quantity < quantity:
                return False
            inventory_item.quantity -= quantity
            inventory_item.last_update = datetime.now()
            session.add(inventory_item)

        if commit:
            session.commit()
        else:
            session.flush()
        return True
    except Exception as e:
        logger.error(f"Error reduciendo stock para producto {product_id}: {str(e)}")
        if commit:
            session.rollback()
        return False


def release_order_stock_once(
    order: Order,
    session: Session,
    new_payment_status: Optional[str] = None,
    commit: bool = True,
) -> bool:
    values: Dict[str, Any] = {"stock_released": True}
    if new_payment_status is not None:
        values["payment_status"] = new_payment_status

    stmt = (
        update(Order)
        .where(col(Order.id) == order.id, col(Order.stock_released).is_(False))
        .values(**values)
    )
    result = session.exec(stmt)
    if result.rowcount != 1:
        return False

    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()
    for item in order_items:
        restore_stock(
            item.product_id,
            item.quantity,
            session,
            variant_id=item.variant_id,
            commit=False,
        )

    if commit:
        session.commit()
    else:
        session.flush()
    session.refresh(order)
    return True
