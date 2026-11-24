from datetime import datetime, timezone
from typing import Optional, List
from pydantic import computed_field, field_validator
from sqlmodel import SQLModel, Field, Relationship

ALLOWED_INSTALLMENTS = (1, 3)
DEFAULT_MAX_INSTALLMENTS = 3
MIN_DISCOUNT_PERCENTAGE = 1
MAX_DISCOUNT_PERCENTAGE = 90
MAX_PROMO_LABEL_LENGTH = 20


def _normalize_utc_naive(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class ProductBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    genero: Optional[str] = "unisex"
    estado: Optional[str] = "nuevo"
    categoria: Optional[str] = None  # Nueva campo para categoría
    edad_destino: Optional[str] = "adulto"
    is_unique: bool = Field(default=False, description="True if product has only one variant combination")
    # For unique products, store the single variant attributes directly
    color: Optional[str] = None
    talle: Optional[str] = None
    stock: Optional[int] = None
    # Discount fields
    has_discount: bool = Field(default=False, description="True if product has a discount")
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100, description="Discount percentage (1-90)")
    promo_label: Optional[str] = Field(default=None, max_length=MAX_PROMO_LABEL_LENGTH, description="Etiqueta opcional de promoción")
    discount_starts_at: Optional[datetime] = Field(default=None, description="Inicio opcional del descuento (UTC)")
    discount_ends_at: Optional[datetime] = Field(default=None, description="Fin opcional del descuento (UTC)")
    max_installments: int = Field(default=DEFAULT_MAX_INSTALLMENTS, description="Cuotas máximas sin interés (1 o 3)")

    @field_validator("max_installments")
    @classmethod
    def _validate_max_installments(cls, v: int) -> int:
        if v not in ALLOWED_INSTALLMENTS:
            raise ValueError("Las cuotas máximas deben ser 1 o 3")
        return v

    def is_discount_active(self, now: Optional[datetime] = None) -> bool:
        if not self.has_discount or self.discount_percentage is None:
            return False
        if self.discount_percentage < MIN_DISCOUNT_PERCENTAGE or self.discount_percentage > MAX_DISCOUNT_PERCENTAGE:
            return False
        current = _normalize_utc_naive(now) or datetime.utcnow()
        start = _normalize_utc_naive(self.discount_starts_at)
        end = _normalize_utc_naive(self.discount_ends_at)
        if start is not None and current < start:
            return False
        if end is not None and current > end:
            return False
        return True

    def effective_price(self, now: Optional[datetime] = None) -> float:
        if self.is_discount_active(now) and self.discount_percentage is not None:
            return float(round(self.price * (1 - self.discount_percentage / 100)))
        return float(self.price)

    def active_discount_amount(self, now: Optional[datetime] = None) -> float:
        if self.is_discount_active(now):
            return round(float(self.price) - self.effective_price(now), 2)
        return 0.0

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    images: List["ProductImage"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    variants: List["ProductVariant"] = Relationship(
        back_populates="product", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # Relationship with OrderItem
    order_items: List["OrderItem"] = Relationship(back_populates="product")

class ProductImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    image_url: str
    
    product: Product = Relationship(back_populates="images")

class ProductVariant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    color: Optional[str] = None
    talle: Optional[str] = None
    stock: int
    
    product: Product = Relationship(back_populates="variants")

class ProductCreate(ProductBase):
    images: List[str]  # List of image URLs
    variants: List["ProductVariantCreate"] = Field(default_factory=list)
    
    def model_validate_unique_product(self):
        """Validate that unique products have proper attributes"""
        if self.is_unique:
            # For unique products, ensure we have the basic attributes
            if not self.color and not self.talle:
                raise ValueError("Unique products must have at least color or size specified")
            if self.stock is None:
                raise ValueError("Unique products must have stock specified")
            # Clear variants array for unique products
            self.variants = []
        else:
            # For variant products, ensure variants are provided
            if not self.variants:
                raise ValueError("Non-unique products must have at least one variant")
            # Clear individual attributes for variant products
            self.color = None
            self.talle = None
            self.stock = None
        
        # Validate discount fields
        if self.has_discount:
            if self.discount_percentage is None:
                raise ValueError("Ingresá un porcentaje de descuento entre 1 y 90")
            if self.discount_percentage < MIN_DISCOUNT_PERCENTAGE or self.discount_percentage > MAX_DISCOUNT_PERCENTAGE:
                raise ValueError("El porcentaje de descuento debe estar entre 1 y 90")
            if self.promo_label is not None:
                cleaned = self.promo_label.strip()
                if len(cleaned) > MAX_PROMO_LABEL_LENGTH:
                    raise ValueError("La etiqueta de promoción no puede superar los 20 caracteres")
                self.promo_label = cleaned or None
            self.discount_starts_at = _normalize_utc_naive(self.discount_starts_at)
            self.discount_ends_at = _normalize_utc_naive(self.discount_ends_at)
            if (
                self.discount_starts_at is not None
                and self.discount_ends_at is not None
                and self.discount_ends_at < self.discount_starts_at
            ):
                raise ValueError("La fecha de fin del descuento debe ser posterior a la de inicio")
        else:
            self.discount_percentage = None
            self.promo_label = None
            self.discount_starts_at = None
            self.discount_ends_at = None

class ProductVariantCreate(SQLModel):
    id: Optional[int] = None
    color: str = Field(min_length=1, description="Color is required for variants")
    talle: str = Field(min_length=1, description="Size is required for variants")  
    stock: int = Field(ge=0)


class ProductImageRead(SQLModel):
    id: int
    image_url: str

class ProductVariantRead(SQLModel):
    id: int
    color: Optional[str]
    talle: Optional[str]
    stock: int

class StockCheckItem(SQLModel):
    """Item para verificación de stock"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(gt=0, description="Cantidad solicitada")

class StockCheckResultItem(SQLModel):
    """Resultado de verificación de stock para un ítem"""
    product_id: int
    variant_id: Optional[int] = None
    available: bool
    available_stock: int
    requested_quantity: int
    has_enough_stock: bool

class StockCheckResponse(SQLModel):
    """Respuesta de verificación de stock"""
    items: List[StockCheckResultItem]
    all_available: bool

class ProductRead(ProductBase):
    id: int
    images: List[ProductImageRead]
    variants: List[ProductVariantRead]
    
    @property
    def display_stock(self) -> int:
        """Return stock for display purposes"""
        if self.is_unique:
            return self.stock or 0
        else:
            return sum(variant.stock for variant in self.variants)
    
    @computed_field
    @property
    def discount_active(self) -> bool:
        """True when discount is enabled and within optional date window."""
        return self.is_discount_active()

    @computed_field
    @property
    def discounted_price(self) -> float:
        """Return effective price rounded to whole pesos when discount is active."""
        return self.effective_price()

    @computed_field
    @property
    def discount_amount(self) -> float:
        """Return active discount amount in currency."""
        return self.active_discount_amount()