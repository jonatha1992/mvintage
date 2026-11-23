

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", nullable=False)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    variant_id: Optional[int] = Field(default=None, foreign_key="productvariant.id")
    quantity: int = Field(gt=0, nullable=False)
    price: float = Field(nullable=False)
    
    # Relationships
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")
