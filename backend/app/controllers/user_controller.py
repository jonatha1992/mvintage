import logging
from typing import List, Optional
import threading
import asyncio
from datetime import datetime
from sqlmodel import Session, select
from app.models.user import User, UserCreate
from app.models.role import Role
from app.models.user_role import UserRole
from sqlalchemy import or_, func
from app.core.config import settings
from app.models.email_verification import EmailVerificationToken
from app.services.notificaciones import CorreoCentralError, notificaciones_service
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def send_welcome_email_async(user_email: str, display_name: Optional[str] = None, client=None):
    """Send welcome email asynchronously in background via correo-central"""
    correo = client or notificaciones_service.client
    nombre = (display_name or user_email.split("@")[0]).strip() or "cliente"
    store_url = (settings.STORE_PUBLIC_URL or settings.APP_URL or "").strip().rstrip("/")
    boton = {"texto": "Ir a la tienda", "url": store_url} if store_url.startswith("https://") else None
    try:
        msg_id = correo.send_bienvenida(
            to=user_email,
            subject=f"¡Bienvenido a {settings.APP_NAME}!",
            nombre=nombre,
            mensaje=f"Tu cuenta en {settings.APP_NAME} ya está lista. Ya podés explorar el catálogo y seguir tus pedidos.",
            boton=boton,
            idempotency_key=f"mvintage:welcome:{user_email.lower().strip()}",
        )
        if msg_id:
            logger.info("Email de bienvenida enviado a %s (id=%s)", user_email, msg_id)
        else:
            logger.warning("Email de bienvenida omitido para %s (correo-central no configurado)", user_email)
    except (CorreoCentralError, Exception) as exc:
        logger.error("Error enviando email de bienvenida a %s: %s", user_email, exc)


def trigger_welcome_email(user_email: str, display_name: Optional[str] = None):
    """Trigger welcome email in background thread"""
    try:
        email_thread = threading.Thread(
            target=send_welcome_email_async,
            args=(user_email, display_name),
            daemon=True,
        )
        email_thread.start()
    except Exception as exc:
        logger.error("Error iniciando envío de email de bienvenida a %s: %s", user_email, exc)


def send_verification_email_async(
    user_id: int,
    user_email: str,
    display_name: Optional[str] = None,
    client=None,
    db: Optional[Session] = None,
):
    """Send verification email asynchronously in background via correo-central"""
    owns_session = db is None
    session: Optional[Session] = db
    try:
        if session is None:
            from app.db.session import get_session

            session = next(get_session())
        assert session is not None

        existing_tokens = session.exec(
            select(EmailVerificationToken).where(
                EmailVerificationToken.email == user_email,
                EmailVerificationToken.used_at == None,  # noqa: E711
            )
        ).all()

        for token in existing_tokens:
            token.mark_as_used()
            session.add(token)

        verification_token = EmailVerificationToken.generate_verification_token(
            user_id=user_id,
            email=user_email,
        )
        session.add(verification_token)
        session.commit()
        session.refresh(verification_token)

        frontend_url = (settings.FRONTEND_URL or settings.STORE_PUBLIC_URL or "").strip().rstrip("/")
        verification_url = f"{frontend_url}/verify-email?token={verification_token.token}"
        saludo = f"Hola {display_name.strip()}," if display_name and display_name.strip() else "Hola,"
        mensaje = (
            f"{saludo}\n\n"
            f"Ingresá este código para verificar tu cuenta en {settings.APP_NAME}.\n"
            f"También podés verificar tu email abriendo este enlace:\n{verification_url}"
        )

        correo = client or notificaciones_service.client
        msg_id = correo.send_codigo(
            to=user_email,
            subject=f"Verificá tu email - {settings.APP_NAME}",
            codigo=verification_token.code,
            vencimiento="24 horas",
            titulo="Verificá tu email",
            mensaje=mensaje,
            idempotency_key=f"mvintage:verify:{verification_token.id or verification_token.code}",
        )
        if msg_id:
            logger.info("Email de verificación enviado a %s (id=%s)", user_email, msg_id)
        else:
            logger.warning("Email de verificación omitido para %s (correo-central no configurado)", user_email)
    except (CorreoCentralError, Exception) as exc:
        logger.error("Error enviando email de verificación a %s: %s", user_email, exc)
    finally:
        if owns_session and session is not None:
            session.close()


def trigger_verification_email(user_id: int, user_email: str, display_name: Optional[str] = None):
    """Trigger verification email in background thread"""
    try:
        email_thread = threading.Thread(
            target=send_verification_email_async,
            args=(user_id, user_email, display_name),
            daemon=True,
        )
        email_thread.start()
    except Exception as exc:
        logger.error("Error iniciando envío de email de verificación a %s: %s", user_email, exc)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.exec(select(User).where(User.username == username)).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.exec(select(User).where(User.email == email)).first()

def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
    return db.exec(select(User).where(User.firebase_uid == firebase_uid)).first()

def create_user_from_firebase(db: Session, firebase_user: dict) -> User:
    # Verificar si ya existe un usuario con este email
    existing_user = get_user_by_email(db, firebase_user['email'])
    if existing_user:
        # Si existe pero sin firebase_uid, actualizar el registro
        if not existing_user.firebase_uid:
            existing_user.firebase_uid = firebase_user['uid']
            existing_user.nombre = firebase_user.get('name') or existing_user.nombre
            if firebase_user.get('email_verified', False):
                existing_user.email_verified = True
                existing_user.email_verified_at = datetime.utcnow()
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # Si ya tiene firebase_uid diferente, es un conflicto
            raise HTTPException(
                status_code=400, 
                detail=f"Email {firebase_user['email']} already exists with different Firebase account"
            )
    
    # Verificar si es el primer usuario en el sistema
    user_count = db.exec(select(func.count(User.id))).first()
    is_first_user = user_count == 0
    
    new_user = User(
        firebase_uid=firebase_user['uid'],
        email=firebase_user['email'],
        username=firebase_user.get('email', '').split('@')[0] if firebase_user.get('email') else None,
        nombre=firebase_user.get('name') # Opcional, si viene de Firebase
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Si es el primer usuario, asignarle automáticamente el rol de admin
    if is_first_user:
        admin_role = db.exec(select(Role).where(Role.name == "admin")).first()
        if admin_role:
            user_role = UserRole(
                user_id=new_user.id,
                role_id=admin_role.id,
                assigned_by=None  # Auto-asignado para el primer usuario
            )
            db.add(user_role)
            db.commit()
            print(f"✅ Primer usuario creado con rol de administrador: {new_user.email}")
        else:
            print("⚠️ Rol de admin no encontrado. Ejecute primero la inicialización de roles.")
    else:
        # Para todos los demás usuarios, asignar el rol de USER por defecto
        user_role_def = db.exec(select(Role).where(Role.name == "user")).first()
        if user_role_def:
            user_role = UserRole(
                user_id=new_user.id,
                role_id=user_role_def.id,
                assigned_by=None # Auto-asignado
            )
            db.add(user_role)
            db.commit()
            print(f"✅ Nuevo usuario '{new_user.email}' asignado con rol por defecto 'USER'.")
        else:
            print(f"⚠️ Rol 'USER' no encontrado para el usuario '{new_user.email}'. Ejecute la inicialización de roles.")

    # For Google users, mark email as verified since Google already verified it
    if firebase_user.get('email_verified', False):
        new_user.email_verified = True
        new_user.email_verified_at = datetime.utcnow()
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Send welcome email to verified users
        trigger_welcome_email(
            user_email=new_user.email,
            display_name=firebase_user.get('name') or firebase_user.get('email', '').split('@')[0]
        )
    else:
        # For email/password users, send verification email
        trigger_verification_email(
            user_id=new_user.id,
            user_email=new_user.email,
            display_name=firebase_user.get('name') or firebase_user.get('email', '').split('@')[0]
        )

    return new_user
    
def create_user(db: Session, user_create: UserCreate) -> User:
    # Esta función se mantiene por si se quiere crear un usuario con el método tradicional
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=user_create.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_all_users(db: Session) -> List[User]:
    return db.exec(select(User)).all()

def search_users(db: Session, query: str) -> List[User]:
    search_pattern = f"%{query}%"
    return db.exec(select(User).where(
        or_(
            User.username.ilike(search_pattern),
            User.email.ilike(search_pattern)
        )
    )).all()

def make_user_admin(db: Session, user_id: int, assigned_by_id: Optional[int] = None) -> bool:
    """Asignar rol de admin a un usuario específico"""
    user = db.get(User, user_id)
    if not user:
        return False
    
    admin_role = db.exec(select(Role).where(Role.name == "admin")).first()
    if not admin_role:
        return False
    
    # Verificar si ya tiene el rol de admin
    existing_role = db.exec(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == admin_role.id,
            UserRole.is_active == True
        )
    ).first()
    
    if existing_role:
        return True  # Ya es admin
    
    # Asignar rol de admin
    user_role = UserRole(
        user_id=user_id,
        role_id=admin_role.id,
        assigned_by=assigned_by_id
    )
    db.add(user_role)
    db.commit()
    return True

def create_user_with_role(db: Session, user_create: UserCreate, role_name: str) -> User:
    """Crear un usuario y asignarle un rol específico"""
    # Crear el usuario básico
    new_user = User(
        firebase_uid=user_create.uid,
        email=user_create.email,
        username=user_create.username if user_create.username else None,
        is_active=user_create.is_active if user_create.is_active is not None else True,
        email_verified=True,  # Usuario admin inicial tiene email verificado
        email_verified_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Buscar el rol especificado
    role = db.exec(select(Role).where(Role.name == role_name)).first()
    if not role:
        # Si no se encuentra el rol, crear el usuario sin rol
        print(f"⚠️ Rol '{role_name}' no encontrado. Usuario creado sin rol.")
        return new_user
    
    # Asignar el rol al usuario
    user_role = UserRole(
        user_id=new_user.id,
        role_id=role.id,
        assigned_by=None  # Auto-asignado durante la inicialización
    )
    db.add(user_role)
    db.commit()
    
    return new_user