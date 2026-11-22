import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
import os
import json

security = HTTPBearer()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    # Solo evitar inicialización en test si NO hay NINGUNA credencial
    if (settings.ENVIRONMENT == "test" and 
        not settings.FIREBASE_SERVICE_ACCOUNT_KEY and 
        not settings.FIREBASE_PROJECT_ID):
        print("Skipping Firebase initialization in test mode without credentials")
        return
        
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        return
    except ValueError:
        # Firebase not initialized, proceed with initialization
        pass
    
    cred = None
    
    # Option 1: Use individual environment variables (simpler for Railway)
    if (settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY and 
        settings.FIREBASE_CLIENT_EMAIL):
        try:
            service_account_info = {
                "type": settings.FIREBASE_TYPE,
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL.replace('@', '%40')}",
                "universe_domain": "googleapis.com"
            }
            cred = credentials.Certificate(service_account_info)
            print("Using individual Firebase environment variables")
        except Exception as e:
            print(f"Error with individual Firebase variables: {e}")
    
    # Option 2: Use environment variable JSON (fallback)
    if not cred and settings.FIREBASE_SERVICE_ACCOUNT_KEY:
        try:
            service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
            cred = credentials.Certificate(service_account_info)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in FIREBASE_SERVICE_ACCOUNT_KEY")
    
    # Option 3: Use local file (for development)
    if not cred:
        cred_path = os.path.join(
            os.path.dirname(__file__), "..", "..", 
            "firebase_service_account.json"
        )
        
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            print("Using local Firebase service account file")
        else:
            print(f"No local Firebase service account file found at {cred_path}")
    
    if cred:
        try:
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
    else:
        print("Warning: No Firebase credentials found")

# Initialize Firebase when module is imported
initialize_firebase()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    import logging
    logger = logging.getLogger(__name__)
    
    if not credentials:
        logger.error("No authorization header provided")
        raise HTTPException(status_code=401, detail="No authorization header")
    
    token = credentials.credentials
    
    try:
        # Check if Firebase Admin SDK is initialized
        try:
            firebase_admin.get_app()
            decoded_token = auth.verify_id_token(token)
        except ValueError:
            # Fallback: verify Firebase ID token using Google public certs (no service account needed)
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests
            decoded_token = google_id_token.verify_firebase_token(
                token,
                google_requests.Request(),
                audience=settings.FIREBASE_PROJECT_ID,
            )
            if not decoded_token:
                raise HTTPException(status_code=401, detail="Invalid Firebase token")
            decoded_token.setdefault('uid', decoded_token.get('user_id') or decoded_token.get('sub'))
        logger.info(f"Token verified successfully for UID: {decoded_token.get('uid')}")
        return decoded_token
    except auth.InvalidIdTokenError as e:
        logger.error(f"Invalid Firebase token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")
    except auth.ExpiredIdTokenError as e:
        logger.error(f"Expired Firebase token: {str(e)}")
        raise HTTPException(status_code=401, detail="Firebase token has expired")
    except auth.RevokedIdTokenError as e:
        logger.error(f"Revoked Firebase token: {str(e)}")
        raise HTTPException(status_code=401, detail="Firebase token has been revoked")
    except Exception as e:
        logger.error(f"Unexpected error verifying Firebase token: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Token verification error: {str(e)}")
