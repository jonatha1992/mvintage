
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, col, select

from app.db.session import get_session
from app.models.order_item import OrderItem
from app.models.product import (
    Product, ProductCreate, ProductRead, ProductImage, ProductVariant,
    ProductVariantCreate, ProductImageRead, ProductVariantRead,
    StockCheckItem, StockCheckResponse, StockCheckResultItem
)
from app.core.security import get_current_user, require_manager_or_admin

router = APIRouter()

@router.post("/products/", response_model=ProductRead)
def create_product(
    session: Session = Depends(get_session), 
    product: ProductCreate = Body(...), 
    current_user=Depends(require_manager_or_admin())
):
    # Validate product data based on type
    try:
        product.model_validate_unique_product()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Separate the main product data from the related images and variants
    product_data = product.model_dump(exclude={'images', 'variants'})
    db_product = Product(**product_data)

    # Create ProductImage objects and link them to the product
    db_product.images = [ProductImage(image_url=url) for url in product.images]
    
    # For non-unique products, create ProductVariant objects
    if not product.is_unique:
        db_product.variants = [ProductVariant(**variant.model_dump(exclude={"id"})) for variant in product.variants]
    else:
        # For unique products, variants are empty (handled by the product attributes)
        db_product.variants = []

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    
    return db_product

@router.get("/products/", response_model=List[ProductRead])
def read_products(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    products = session.exec(select(Product).offset(skip).limit(limit)).all()
    return [ProductRead.model_validate(p) for p in products]

@router.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead.model_validate(product)

@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, 
    session: Session = Depends(get_session), 
    product: ProductCreate = Body(...), 
    current_user=Depends(require_manager_or_admin())
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate product data based on type
    try:
        product.model_validate_unique_product()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    existing_variants = list(db_product.variants)
    existing_by_id = {v.id: v for v in existing_variants if v.id is not None}
    variants_to_update: list[tuple[ProductVariant, ProductVariantCreate]] = []
    variants_to_create: list[ProductVariantCreate] = []
    matched_ids: set[int] = set()

    if not product.is_unique:
        unmatched_by_key: dict[tuple[str | None, str | None], list[ProductVariant]] = {}
        for incoming in product.variants:
            if incoming.id is not None:
                existing = existing_by_id.get(incoming.id)
                if existing is None or existing.id in matched_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"La variante {incoming.id} no pertenece al producto {product_id}",
                    )
                matched_ids.add(existing.id)
                variants_to_update.append((existing, incoming))

        for v in existing_variants:
            if v.id is not None and v.id not in matched_ids:
                unmatched_by_key.setdefault((v.color, v.talle), []).append(v)

        for incoming in product.variants:
            if incoming.id is None:
                bucket = unmatched_by_key.get((incoming.color, incoming.talle))
                if bucket:
                    existing = bucket.pop(0)
                    if existing.id is not None:
                        matched_ids.add(existing.id)
                    variants_to_update.append((existing, incoming))
                else:
                    variants_to_create.append(incoming)

    variants_to_remove = [
        v for v in existing_variants if v.id is None or v.id not in matched_ids
    ]
    remove_ids = [v.id for v in variants_to_remove if v.id is not None]
    if remove_ids:
        used_variant_ids = set(
            session.exec(
                select(OrderItem.variant_id)
                .where(col(OrderItem.variant_id).in_(remove_ids))
                .distinct()
            ).all()
        )
        if used_variant_ids:
            blocked = [v for v in variants_to_remove if v.id in used_variant_ids]
            labels = ", ".join(
                f"{v.color or '-'} / {v.talle or '-'}" for v in blocked
            )
            raise HTTPException(
                status_code=409,
                detail=(
                    f"No se puede eliminar la variante ({labels}) porque tiene pedidos asociados. "
                    "Podés dejar su stock en 0."
                ),
            )

    product_data = product.model_dump(exclude_unset=True, exclude={'images', 'variants'})
    for key, value in product_data.items():
        setattr(db_product, key, value)

    existing_images = list(db_product.images)
    desired_urls = list(product.images)
    if [img.image_url for img in existing_images] != desired_urls:
        existing_by_url: dict[str, list[ProductImage]] = {}
        for img in existing_images:
            existing_by_url.setdefault(img.image_url, []).append(img)
        synced_images: list[ProductImage] = []
        for url in desired_urls:
            bucket = existing_by_url.get(url)
            if bucket:
                synced_images.append(bucket.pop(0))
            else:
                synced_images.append(ProductImage(product_id=db_product.id, image_url=url))
        db_product.images = synced_images

    for existing, incoming in variants_to_update:
        existing.color = incoming.color
        existing.talle = incoming.talle
        existing.stock = incoming.stock

    for variant in variants_to_remove:
        db_product.variants.remove(variant)

    for incoming in variants_to_create:
        db_product.variants.append(
            ProductVariant(
                product_id=db_product.id,
                color=incoming.color,
                talle=incoming.talle,
                stock=incoming.stock,
            )
        )

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session), current_user=Depends(require_manager_or_admin())):
    """Eliminar un producto y todos sus datos relacionados"""
    from sqlmodel import select
    
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Primero eliminar las imágenes relacionadas
    from app.models.product import ProductImage, ProductVariant
    images = session.exec(select(ProductImage).where(ProductImage.product_id == product_id)).all()
    for image in images:
        session.delete(image)
    
    # Luego eliminar las variantes relacionadas
    variants = session.exec(select(ProductVariant).where(ProductVariant.product_id == product_id)).all()
    for variant in variants:
        session.delete(variant)
    
    # Finalmente eliminar el producto
    session.delete(product)
    session.commit()
    return {"ok": True, "message": "Product and related data deleted successfully"}

@router.post("/products/check-stock/", response_model=StockCheckResponse)
async def check_stock(
    items: List[StockCheckItem],
    session: Session = Depends(get_session)
):
    """
    Verifica el stock disponible para múltiples productos/variantes.
    
    Args:
        items: Lista de ítems a verificar, cada uno con product_id, variant_id opcional y cantidad
        
    Returns:
        StockCheckResponse: Resultado de la verificación de stock para cada ítem
    """
    results = []
    all_available = True
    
    for item in items:
        # Obtener el producto
        product = session.get(Product, item.product_id)
        if not product:
            results.append(StockCheckResultItem(
                product_id=item.product_id,
                variant_id=item.variant_id,
                available=False,
                available_stock=0,
                requested_quantity=item.quantity,
                has_enough_stock=False
            ))
            all_available = False
            continue
            
        # Verificar stock según si es producto único o con variantes
        if product.is_unique:
            # Producto único - verificar stock directo
            available_stock = product.stock or 0
            has_enough = available_stock >= item.quantity
            
            results.append(StockCheckResultItem(
                product_id=item.product_id,
                variant_id=None,
                available=available_stock > 0,
                available_stock=available_stock,
                requested_quantity=item.quantity,
                has_enough_stock=has_enough
            ))
            
            if not has_enough:
                all_available = False
                
        else:
            # Producto con variantes - verificar stock de la variante específica
            if not item.variant_id:
                # Si no se proporciona variant_id para producto con variantes, error
                results.append(StockCheckResultItem(
                    product_id=item.product_id,
                    variant_id=None,
                    available=False,
                    available_stock=0,
                    requested_quantity=item.quantity,
                    has_enough_stock=False
                ))
                all_available = False
                continue
                
            # Buscar la variante
            variant = session.get(ProductVariant, item.variant_id)
            if not variant or variant.product_id != product.id:
                results.append(StockCheckResultItem(
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    available=False,
                    available_stock=0,
                    requested_quantity=item.quantity,
                    has_enough_stock=False
                ))
                all_available = False
                continue
                
            # Verificar stock de la variante
            has_enough = variant.stock >= item.quantity
            results.append(StockCheckResultItem(
                product_id=item.product_id,
                variant_id=item.variant_id,
                available=variant.stock > 0,
                available_stock=variant.stock,
                requested_quantity=item.quantity,
                has_enough_stock=has_enough
            ))
            
            if not has_enough:
                all_available = False
    
    return StockCheckResponse(items=results, all_available=all_available)
