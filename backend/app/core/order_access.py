import hashlib
import hmac
from urllib.parse import urlencode

from fastapi import Depends, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.auth_firebase import verify_firebase_token
from app.core.config import settings
from app.db.session import get_session
from app.models.order import Order

optional_bearer = HTTPBearer(auto_error=False)


def order_access_token(order_id: int) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        f"order-access:v1:{order_id}".encode(),
        hashlib.sha256,
    ).hexdigest()


def order_public_url(order_id: int, site_url: str) -> str:
    query = urlencode({"access_token": order_access_token(order_id)})
    return f"{site_url.rstrip('/')}/orders/{order_id}?{query}"


def optional_order_user(
    credentials: HTTPAuthorizationCredentials | None = Security(optional_bearer),
    access_token: str | None = Query(default=None, max_length=128),
):
    if access_token is not None or credentials is None:
        return None
    return verify_firebase_token(credentials)


def get_accessible_order(
    order_id: int,
    access_token: str | None = Query(default=None, max_length=128),
    user=Depends(optional_order_user),
    session: Session = Depends(get_session),
) -> Order:
    from app.core.security import check_order_ownership_or_admin

    if access_token is not None:
        if not hmac.compare_digest(access_token.encode(), order_access_token(order_id).encode()):
            raise HTTPException(status_code=403, detail="El enlace del pedido no es válido")
    elif user is None:
        raise HTTPException(status_code=401, detail="Iniciá sesión o usá el enlace de tu pedido")
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if access_token is None:
        check_order_ownership_or_admin(order, user, session)
    return order
