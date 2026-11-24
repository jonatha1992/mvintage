import html
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.rate_limit import rate_limit
from app.services.notificaciones import CorreoCentralError, NotificacionesService, notificaciones_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ContactMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=254)
    mensaje: str = Field(min_length=10, max_length=4000)


def get_notifications() -> NotificacionesService:
    return notificaciones_service


@router.post("/contact", dependencies=[Depends(rate_limit("contact", limit=3, window_seconds=600))])
def contact(payload: ContactMessage, notifications: NotificacionesService = Depends(get_notifications)):
    if not notifications.client.is_configured:
        raise HTTPException(503, "No pudimos enviar tu mensaje. Escribinos por WhatsApp.")
    try:
        message_id = notifications.client.send_aviso(
            to=notifications.owner_email,
            subject="Consulta desde la tienda - Showroom Isabella",
            titulo="Nueva consulta de contacto",
            mensaje=html.escape(f"Nombre: {payload.nombre}\nEmail: {payload.email}\n\n{payload.mensaje}"),
            reply_to=str(payload.email),
            idempotency_key=f"showroomisabella-contact-{uuid4()}",
        )
    except CorreoCentralError:
        logger.exception("No se pudo entregar la consulta a correo-central")
        raise HTTPException(502, "No pudimos enviar tu mensaje. Escribinos por WhatsApp.") from None
    if not message_id:
        raise HTTPException(503, "No pudimos enviar tu mensaje. Escribinos por WhatsApp.")
    return {"message": "Recibimos tu mensaje. Te responderemos por email."}
