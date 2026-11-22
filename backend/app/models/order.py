
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    status: Optional[str] = None
    shipping_status: str = Field(default="pending", max_length=20, description="pending, prepared, ready_to_ship, shipped, in_transit, delivered, failed")
    total: float = Field(ge=0)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Payment fields
    payment_method: str = Field(default="transfer", max_length=20)
    payment_status: str = Field(default="pending", max_length=20)
    mercadopago_payment_id: Optional[str] = Field(default=None)
    mercadopago_preference_id: Optional[str] = Field(default=None)
    
    # Delivery method
    delivery_method: Optional[str] = Field(
        default=None,
        max_length=30,
        description="Modalidad obligatoria. La tienda solo admite retiro_local.",
    )
    
    # Campos para TRANSFERENCIA
    bank_account_info: Optional[str] = Field(default=None, description="JSON con datos bancarios mostrados")
    transfer_receipt_url: Optional[str] = Field(default=None, description="URL del comprobante subido")
    transfer_verified: Optional[bool] = Field(default=None, description="Si admin verificó la transferencia")
    transfer_verification_date: Optional[datetime] = Field(default=None)
    
    # Campos para EFECTIVO
    delivery_cost: Optional[float] = Field(default=None, description="Costo de envío calculado")
    delivery_zone: Optional[str] = Field(default=None, description="Zona de entrega")
    delivery_scheduled_date: Optional[datetime] = Field(default=None, description="Fecha programada")
    delivery_time_slot: Optional[str] = Field(default=None, description="Horario: mañana, tarde")
    delivery_status: Optional[str] = Field(default=None, description="pending, scheduled, in_transit, delivered")
    delivery_notes: Optional[str] = Field(default=None, description="Notas del delivery")
    
    # Campos ADMIN generales
    admin_notes: Optional[str] = Field(default=None, description="Notas del administrador")
    verification_required: bool = Field(default=False, description="Si requiere verificación manual")
    verified_by_admin: Optional[bool] = Field(default=None, description="Si admin verificó")
    admin_verification_date: Optional[datetime] = Field(default=None)
    
    # Campos de SEGUIMIENTO DE ENVÍO
    tracking_number: Optional[str] = Field(default=None, max_length=255, description="Número de seguimiento del proveedor")
    shipping_provider: Optional[str] = Field(default=None, max_length=100, description="Proveedor: correo-argentino, oca, andreani")
    shipped_at: Optional[datetime] = Field(default=None, description="Fecha y hora de envío")
    estimated_delivery: Optional[datetime] = Field(default=None, description="Fecha estimada de entrega")
    shipped_by: Optional[int] = Field(default=None, foreign_key="user.id", description="Admin que marcó como enviado")
    tracking_updated_at: Optional[datetime] = Field(default=None, description="Última actualización del tracking")
    delivery_notes_shipping: Optional[str] = Field(default=None, description="Notas específicas del envío")
    
    # Relationship with OrderItem
    items: List["OrderItem"] = Relationship(back_populates="order", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
