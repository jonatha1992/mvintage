from typing import Optional, List
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

ALLOWED_INSTALLMENTS = (1, 3, 6, 12)
DEFAULT_MAX_INSTALLMENTS = 3

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
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100, description="Discount percentage (0-100)")
    max_installments: int = Field(default=DEFAULT_MAX_INSTALLMENTS, description="Max installments offered (1, 3, 6, 12)")

    @field_validator("max_installments")
    @classmethod
    def _validate_max_installments(cls, v: int) -> int:
        if v not in ALLOWED_INSTALLMENTS:
            raise ValueError("max_installments must be one of 1, 3, 6, 12")
        return v

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
                raise ValueError("Products with discount must have a discount percentage specified")
            if self.discount_percentage <= 0 or self.discount_percentage > 100:
                raise ValueError("Discount percentage must be between 1 and 100")
        else:
            # If no discount, clear the percentage
            self.discount_percentage = None

class ProductVariantCreate(SQLModel):
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
    
    @property
    def discounted_price(self) -> float:
        """Return price with discount applied if applicable"""
        if self.has_discount and self.discount_percentage:
            discount_amount = self.price * (self.discount_percentage / 100)
            return round(self.price - discount_amount, 2)
        return self.price
    
    @property
    def discount_amount(self) -> float:
        """Return the discount amount in currency"""
        if self.has_discount and self.discount_percentage:
            return round(self.price * (self.discount_percentage / 100), 2)
        return 0.0