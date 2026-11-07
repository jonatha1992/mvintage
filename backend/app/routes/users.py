from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.models.user import User, UserRead, UserWithRoles
from app.controllers.user_controller import get_user_by_firebase_uid, create_user_from_firebase, get_all_users
from app.core.auth_firebase import verify_firebase_token
from app.controllers.role_controller import get_user_roles, assign_role_to_user
from app.core.security import require_manager_or_admin
from firebase_admin import auth as firebase_auth
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["Users"])

class CreateUserRequest(BaseModel):
    email: str
    password: str
    username: str = None
    role_id: int

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

@router.get("/debug-all", response_model=dict)
def debug_all_users(
    db: Session = Depends(get_session),
    current_user= Depends(require_manager_or_admin())
):
    users = get_all_users(db)
    data = []
    for u in users:
        data.append({
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "firebase_uid": u.firebase_uid,
            "is_active": u.is_active
        })
    return {"count": len(data), "users": data}

@router.post("/sync", response_model=dict)
def sync_firebase_users(
    db: Session = Depends(get_session),
    current_user= Depends(require_manager_or_admin())
):
    """Importar todos los usuarios de Firebase Auth que no existan aún en la DB.
    Crea registros con email y firebase_uid; no asigna roles salvo primer usuario (regla existente).
    """
    imported = 0
    page_token = None
    try:
        while True:
            page = firebase_auth.list_users(page_token=page_token)
            for u in page.users:
                if not u.email:
                    continue
                found = db.exec(select(User).where(User.firebase_uid == u.uid)).first()
                if found:
                    continue
                user_obj = User(firebase_uid=u.uid, email=u.email, username=u.display_name)
                db.add(user_obj)
                try:
                    db.commit()
                    imported += 1
                except IntegrityError:
                    db.rollback()
            page_token = page.next_page_token
            if not page_token:
                break
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sincronizando usuarios: {e}")
    total = len(db.exec(select(User)).all())
    return {"imported": imported, "total_users": total}

@router.post("/create", response_model=dict)
def create_new_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_session),
    current_user= Depends(require_manager_or_admin())
):
    """Crear un nuevo usuario en Firebase Auth y en la base de datos local con rol específico."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log del intento de creación (sin password)
    logger.info(f"Attempting to create user: email={user_data.email}, username={user_data.username}, role_id={user_data.role_id}")
    
    try:
        # Verificar si el email ya existe en la base de datos local
        existing_user = db.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            logger.warning(f"User creation failed: Email {user_data.email} already exists in local database")
            raise HTTPException(status_code=400, detail="El email ya está registrado en la base de datos")
        
        # 1. Crear usuario en Firebase Auth
        logger.info(f"Creating Firebase user for email: {user_data.email}")
        firebase_user = firebase_auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.username
        )
        logger.info(f"Firebase user created successfully: uid={firebase_user.uid}")
        
        # 2. Crear usuario en la base de datos local
        logger.info(f"Creating local database user for Firebase UID: {firebase_user.uid}")
        new_user = User(
            firebase_uid=firebase_user.uid,
            email=user_data.email,
            username=user_data.username,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Local user created successfully: id={new_user.id}")
        
        # 3. Asignar el rol especificado
        logger.info(f"Assigning role {user_data.role_id} to user {new_user.id}")
        assign_role_to_user(db, new_user.id, user_data.role_id, current_user.id)
        logger.info(f"Role assigned successfully to user {new_user.id}")
        
        # 4. Send welcome email
        try:
            from app.controllers.user_controller import trigger_welcome_email
            trigger_welcome_email(
                user_email=new_user.email,
                display_name=user_data.username or user_data.email.split('@')[0]
            )
            logger.info(f"Welcome email triggered for user {new_user.email}")
        except Exception as email_error:
            logger.error(f"Failed to send welcome email to {new_user.email}: {email_error}")
            # Don't fail user creation if email fails
        
        result = {
            "success": True,
            "message": f"Usuario {user_data.email} creado exitosamente",
            "user_id": new_user.id,
            "firebase_uid": firebase_user.uid
        }
        logger.info(f"User creation completed successfully: {result}")
        return result
        
    except firebase_auth.EmailAlreadyExistsError as e:
        logger.error(f"Firebase email already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="El email ya está registrado en Firebase")
    except firebase_auth.WeakPasswordError as e:
        logger.error(f"Firebase weak password error for email: {user_data.email}")
        raise HTTPException(status_code=400, detail="La contraseña es muy débil. Debe tener al menos 6 caracteres")
    except HTTPException:
        # Re-raise HTTPExceptions (como el check de email duplicado)
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        db.rollback()
        # Si Firebase user fue creado pero falla la DB, debemos limpiarlo
        try:
            if 'firebase_user' in locals():
                firebase_auth.delete_user(firebase_user.uid)
                logger.info(f"Cleaned up Firebase user {firebase_user.uid} due to DB error")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup Firebase user: {cleanup_error}")
        raise HTTPException(status_code=400, detail="Error de integridad en la base de datos. El usuario podría ya existir")
    except Exception as e:
        logger.error(f"Unexpected error creating user {user_data.email}: {str(e)}", exc_info=True)
        db.rollback()
        # Si Firebase user fue creado pero falla algo más, debemos limpiarlo
        try:
            if 'firebase_user' in locals():
                firebase_auth.delete_user(firebase_user.uid)
                logger.info(f"Cleaned up Firebase user {firebase_user.uid} due to unexpected error")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup Firebase user: {cleanup_error}")
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@router.get("/", response_model=list[UserWithRoles])
def list_users(
    db: Session = Depends(get_session),
    current_user= Depends(require_manager_or_admin())
):
    users = get_all_users(db)
    enriched = []
    for u in users:
        roles = get_user_roles(db, u.id)
        role_items = [
            {"id": r.id, "name": r.name, "description": r.description, "is_active": r.is_active}
            for r in roles
        ]
        enriched.append({
            "id": u.id,
            "email": u.email,
            "is_active": u.is_active,
            "username": u.username,
            "firebase_uid": u.firebase_uid,
            "roles": role_items
        })
    return enriched

@router.get("/me", response_model=UserRead)
async def get_or_create_me(
    db: Session = Depends(get_session),
    firebase_user: dict = Depends(verify_firebase_token)
):
    """
    Obtiene el usuario actual a partir del token de Firebase.
    Si el usuario no existe en la base de datos, lo crea.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not firebase_user:
        logger.error("No Firebase user provided to /users/me")
        raise HTTPException(status_code=401, detail="Not authenticated")

    logger.info(f"Getting user for Firebase UID: {firebase_user.get('uid')}")

    try:
        # Buscar usuario por Firebase UID
        user = get_user_by_firebase_uid(db, firebase_user['uid'])

        # Si no existe, crearlo
        if not user:
            logger.info(f"User not found, creating new user for UID: {firebase_user.get('uid')}")
            user = create_user_from_firebase(db, firebase_user)
            logger.info(f"User created successfully: {user.id}")
        else:
            logger.info(f"Existing user found: {user.id}")
        
        return UserRead.from_user(user)
    except Exception as e:
        logger.error(f"Error in /users/me for UID {firebase_user.get('uid')}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing user: {str(e)}")

@router.patch("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdateRequest,
    db: Session = Depends(get_session),
    firebase_user: dict = Depends(verify_firebase_token)
):
    """
    Actualiza la información del usuario actual.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not firebase_user:
        logger.error("No Firebase user provided to PATCH /users/me")
        raise HTTPException(status_code=401, detail="Not authenticated")

    logger.info(f"Updating user for Firebase UID: {firebase_user.get('uid')}")

    try:
        # Buscar usuario por Firebase UID
        user = get_user_by_firebase_uid(db, firebase_user['uid'])
        
        if not user:
            logger.error(f"User not found for UID: {firebase_user.get('uid')}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Actualizar campos si se proporcionan
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
                logger.info(f"Updated {field} for user {user.id}")
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user.id} updated successfully")
        return UserRead.from_user(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user for UID {firebase_user.get('uid')}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.get("/debug", response_model=dict)
async def debug_user_auth(
    db: Session = Depends(get_session),
    firebase_user: dict = Depends(verify_firebase_token)
):
    """
    Endpoint de debug para verificar el estado de autenticación y roles del usuario.
    """
    if not firebase_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Buscar usuario por Firebase UID
    user = get_user_by_firebase_uid(db, firebase_user['uid'])

    # Si no existe, crearlo
    if not user:
        user = create_user_from_firebase(db, firebase_user)

    # Obtener roles del usuario
    roles = get_user_roles(db, user.id)
    role_names = [role.name for role in roles]

    return {
        "firebase_user": {
            "uid": firebase_user.get('uid'),
            "email": firebase_user.get('email'),
            "name": firebase_user.get('name')
        },
        "database_user": {
            "id": user.id,
            "email": user.email,
            "firebase_uid": user.firebase_uid
        },
        "roles": role_names,
        "has_admin_role": any(role.lower() == "admin" for role in role_names),
        "has_manager_role": any(role.lower() == "manager" for role in role_names)
    }

@router.get("/test-auth")
async def test_auth_endpoint():
    """
    Endpoint simple que no requiere autenticación para verificar que el routing funciona.
    """
    return {"message": "Auth endpoint is working", "timestamp": "2025-08-07"}

@router.get("/test-firebase")
async def test_firebase_config():
    """
    Endpoint para verificar la configuración de Firebase sin autenticación.
    """
    import firebase_admin
    from app.core.config import settings
    
    try:
        app_instance = firebase_admin.get_app()
        return {
            "status": "Firebase initialized",
            "app_name": app_instance.name,
            "project_id": app_instance.project_id,
            "environment": settings.ENVIRONMENT,
            "has_firebase_key": bool(settings.FIREBASE_SERVICE_ACCOUNT_KEY),
            "firebase_project_id": settings.FIREBASE_PROJECT_ID
        }
    except ValueError:
        return {
            "status": "Firebase not initialized", 
            "error": "No app instance found",
            "environment": settings.ENVIRONMENT,
            "has_firebase_key": bool(settings.FIREBASE_SERVICE_ACCOUNT_KEY),
            "firebase_project_id": settings.FIREBASE_PROJECT_ID
        }
    except Exception as e:
        return {
            "status": "Firebase error", 
            "error": str(e),
            "environment": settings.ENVIRONMENT,
            "has_firebase_key": bool(settings.FIREBASE_SERVICE_ACCOUNT_KEY),
            "firebase_project_id": settings.FIREBASE_PROJECT_ID
        }
