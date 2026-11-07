from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .role import RoleRead

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    username: Optional[str] = Field(default=None, index=True, unique=True)
    firebase_uid: Optional[str] = Field(default=None, unique=True, index=True)
    nombre: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    
    # Email verification fields
    email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None)
    
    # Relación con UserRole (many-to-many through user_roles)
    user_roles: List["UserRole"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserRole.user_id"}
    )

# Alias para compatibilidad con controladores/rutas
UserDB = User

# DTO para el antiguo sistema de registro. Se mantiene por compatibilidad.
class UserCreate(UserBase):
    password: Optional[str] = None
    uid: Optional[str] = None  # Para compatibilidad con Firebase UID

# DTO para el antiguo sistema de login.
class UserLogin(SQLModel):
    username: str
    password: str

# DTO para enviar los datos del usuario al cliente.
class UserRead(UserBase):
    id: int
    name: Optional[str] = None  # Alias para nombre
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    
    @classmethod
    def from_user(cls, user: "User") -> "UserRead":
        """Crear UserRead desde User con el alias name"""
        return cls(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            username=user.username,
            firebase_uid=user.firebase_uid,
            nombre=user.nombre,
            name=user.nombre,  # Alias
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            email_verified=user.email_verified,
            email_verified_at=user.email_verified_at
        )

class UserWithRoles(UserRead):
    roles: List[RoleRead] = []

# Importación para evitar problemas de importación circular
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user_role import UserRole