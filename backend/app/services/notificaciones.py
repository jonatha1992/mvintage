from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from urllib.parse import quote

import httpx
from sqlmodel import Session, select

from app.core.config import settings
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant

logger = logging.getLogger(__name__)

DEFAULT_CORREO_URL = "https://correo.tecnofusion.dev"
DEFAULT_OWNER_EMAIL = "Showroomisabella@gmail.com"
DEFAULT_WHATSAPP_NUMBER = "5491176372876"
DEFAULT_STORE_PUBLIC_URL = "https://showroomisabella-ar.web.app"
DEFAULT_STORE_PICKUP_ADDRESS = "Alonso Pareja 6542, González Catán (Buenos Aires)"
DEFAULT_TIMEOUT_SECONDS = 5.0

PAYMENT_METHOD_LABELS = {
    "transfer": "Transferencia bancaria",
    "mercadopago": "Mercado Pago",
    "cash": "Efectivo",
}


class CorreoCentralError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class CorreoSender(Protocol):
    @property
    def is_configured(self) -> bool: ...

    def send_aviso(
        self,
        *,
        to: str,
        subject: str,
        titulo: str,
        mensaje: str,
        idempotency_key: str,
        boton: Optional[Dict[str, str]] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]: ...

    def send_bienvenida(
        self,
        *,
        to: str,
        subject: str,
        nombre: str,
        mensaje: Optional[str] = None,
        boton: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]: ...

    def send_codigo(
        self,
        *,
        to: str,
        subject: str,
        codigo: str,
        vencimiento: str,
        titulo: Optional[str] = None,
        mensaje: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]: ...


class CorreoCentralClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        http_client: Optional[httpx.Client] = None,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._timeout = timeout
        self._http_client = http_client

    @property
    def base_url(self) -> str:
        raw = self._base_url if self._base_url is not None else settings.CORREO_CENTRAL_URL
        return (raw or DEFAULT_CORREO_URL).strip().rstrip("/")

    @property
    def api_key(self) -> str:
        raw = self._api_key if self._api_key is not None else settings.CORREO_CENTRAL_API_KEY
        return (raw or "").strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _send_template(
        self,
        *,
        template_id: str,
        template_data: Dict[str, Any],
        to: str,
        subject: str,
        idempotency_key: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        if not self.is_configured:
            logger.warning("Notificaciones por correo desactivadas: falta CORREO_CENTRAL_API_KEY")
            return None

        payload: Dict[str, Any] = {
            "to": to,
            "subject": subject,
            "template": {"id": template_id, "data": template_data},
        }
        if idempotency_key:
            payload["idempotencyKey"] = idempotency_key
        if reply_to:
            payload["replyTo"] = reply_to

        url = f"{self.base_url}/v1/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            if self._http_client is not None:
                response = self._http_client.post(
                    url, json=payload, headers=headers, timeout=self._timeout
                )
            else:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise CorreoCentralError(f"Error de conexión con correo-central: {exc}") from exc

        if response.status_code >= 400:
            raise CorreoCentralError(
                f"correo-central respondió HTTP {response.status_code}",
                status_code=response.status_code,
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise CorreoCentralError("correo-central devolvió una respuesta no JSON") from exc

        message_id = body.get("id") if isinstance(body, dict) else None
        if not isinstance(message_id, str) or not message_id:
            raise CorreoCentralError("correo-central devolvió respuesta sin id")
        return message_id

    def send_aviso(
        self,
        *,
        to: str,
        subject: str,
        titulo: str,
        mensaje: str,
        idempotency_key: str,
        boton: Optional[Dict[str, str]] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        template_data: Dict[str, Any] = {
            "titulo": titulo,
            "mensaje": mensaje,
        }
        if boton:
            template_data["boton"] = boton
        return self._send_template(
            template_id="aviso",
            template_data=template_data,
            to=to,
            subject=subject,
            idempotency_key=idempotency_key,
            reply_to=reply_to,
        )

    def send_bienvenida(
        self,
        *,
        to: str,
        subject: str,
        nombre: str,
        mensaje: Optional[str] = None,
        boton: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        template_data: Dict[str, Any] = {"nombre": nombre}
        if mensaje:
            template_data["mensaje"] = mensaje
        if boton:
            template_data["boton"] = boton
        return self._send_template(
            template_id="bienvenida",
            template_data=template_data,
            to=to,
            subject=subject,
            idempotency_key=idempotency_key,
            reply_to=reply_to,
        )

    def send_codigo(
        self,
        *,
        to: str,
        subject: str,
        codigo: str,
        vencimiento: str,
        titulo: Optional[str] = None,
        mensaje: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Optional[str]:
        template_data: Dict[str, Any] = {
            "codigo": codigo,
            "vencimiento": vencimiento,
        }
        if titulo:
            template_data["titulo"] = titulo
        if mensaje:
            template_data["mensaje"] = mensaje
        return self._send_template(
            template_id="codigo",
            template_data=template_data,
            to=to,
            subject=subject,
            idempotency_key=idempotency_key,
            reply_to=reply_to,
        )


@dataclass(frozen=True)
class OrderItemSnapshot:
    product_name: str
    quantity: int
    price: float
    color: Optional[str] = None
    talle: Optional[str] = None


@dataclass(frozen=True)
class OrderNotificationSnapshot:
    order_id: int
    total: float
    payment_method: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    items: tuple[OrderItemSnapshot, ...] = field(default_factory=tuple)


def is_valid_email(value: Optional[str]) -> bool:
    if not isinstance(value, str):
        return False
    cleaned = value.strip()
    if not cleaned or " " in cleaned or "@" not in cleaned:
        return False
    local, _, domain = cleaned.partition("@")
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def format_ars(amount: float | int) -> str:
    rounded = round(float(amount or 0), 2)
    if rounded.is_integer():
        return f"${int(rounded):,}".replace(",", ".")
    integer_part, decimal_part = f"{rounded:,.2f}".split(".")
    return f"${integer_part.replace(',', '.')},{decimal_part}"


def format_payment_method(method: Optional[str]) -> str:
    key = (method or "").strip().lower()
    return PAYMENT_METHOD_LABELS.get(key, method or "Sin especificar")


def build_whatsapp_url(text: str, phone: Optional[str] = None) -> str:
    number = (phone or settings.NOTIFY_WHATSAPP_NUMBER or DEFAULT_WHATSAPP_NUMBER).strip()
    return f"https://wa.me/{number}?text={quote(text)}"


def _format_items_lines(items: tuple[OrderItemSnapshot, ...]) -> List[str]:
    lines: List[str] = []
    for item in items:
        attrs: List[str] = []
        if item.color:
            attrs.append(f"Color: {item.color}")
        if item.talle:
            attrs.append(f"Talle: {item.talle}")
        variant_text = f" ({', '.join(attrs)})" if attrs else ""
        subtotal = format_ars(item.price * item.quantity)
        lines.append(f"- {item.quantity}x {item.product_name}{variant_text} — {subtotal}")
    return lines


def build_order_snapshot(
    order: Order,
    session: Session,
    customer: Optional[Customer] = None,
) -> Optional[OrderNotificationSnapshot]:
    if order.id is None:
        return None
    resolved_customer = customer or session.get(Customer, order.customer_id)
    if resolved_customer is None:
        return None

    rows = session.exec(
        select(OrderItem, Product)
        .where(OrderItem.order_id == order.id)
        .join(Product, OrderItem.product_id == Product.id)
    ).all()

    items: List[OrderItemSnapshot] = []
    for order_item, product in rows:
        color = product.color
        talle = product.talle
        if order_item.variant_id is not None:
            variant = session.get(ProductVariant, order_item.variant_id)
            if variant is not None:
                color = variant.color or color
                talle = variant.talle or talle
        items.append(
            OrderItemSnapshot(
                product_name=product.name,
                quantity=order_item.quantity,
                price=float(order_item.price),
                color=color,
                talle=talle,
            )
        )

    return OrderNotificationSnapshot(
        order_id=order.id,
        total=float(order.total or 0),
        payment_method=(order.payment_method or "transfer").strip().lower(),
        customer_name=(resolved_customer.name or "Cliente").strip(),
        customer_email=(resolved_customer.email or "").strip() or None,
        customer_phone=(resolved_customer.phone or "").strip() or None,
        items=tuple(items),
    )


class NotificacionesService:
    def __init__(
        self,
        client: Optional[CorreoSender] = None,
        owner_email: Optional[str] = None,
        site_url: Optional[str] = None,
        whatsapp_number: Optional[str] = None,
        pickup_address: Optional[str] = None,
    ):
        self.client: CorreoSender = client or CorreoCentralClient()
        self._owner_email = owner_email
        self._site_url = site_url
        self._whatsapp_number = whatsapp_number
        self._pickup_address = pickup_address

    @property
    def owner_email(self) -> str:
        raw = self._owner_email if self._owner_email is not None else settings.NOTIFY_OWNER_EMAIL
        return (raw or DEFAULT_OWNER_EMAIL).strip()

    @property
    def site_url(self) -> str:
        raw = self._site_url if self._site_url is not None else settings.STORE_PUBLIC_URL
        return (raw or DEFAULT_STORE_PUBLIC_URL).strip().rstrip("/")

    @property
    def whatsapp_number(self) -> str:
        raw = self._whatsapp_number if self._whatsapp_number is not None else settings.NOTIFY_WHATSAPP_NUMBER
        return (raw or DEFAULT_WHATSAPP_NUMBER).strip()

    @property
    def pickup_address(self) -> str:
        raw = self._pickup_address if self._pickup_address is not None else settings.STORE_PICKUP_ADDRESS
        return (raw or DEFAULT_STORE_PICKUP_ADDRESS).strip()

    def _safe_send(
        self,
        *,
        role: str,
        event: str,
        order_id: int,
        to: str,
        subject: str,
        titulo: str,
        mensaje: str,
        idempotency_key: str,
        boton: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        if not is_valid_email(to):
            logger.warning(
                "Destinatario inválido para pedido #%s (%s/%s)",
                order_id,
                event,
                role,
            )
            return None
        try:
            msg_id = self.client.send_aviso(
                to=to,
                subject=subject,
                titulo=titulo,
                mensaje=mensaje,
                idempotency_key=idempotency_key,
                boton=boton,
            )
            if msg_id:
                logger.info(
                    "Correo enviado pedido=#%s event=%s role=%s id=%s",
                    order_id,
                    event,
                    role,
                    msg_id,
                )
            return msg_id
        except Exception as exc:
            logger.error(
                "Error enviando correo pedido=#%s event=%s role=%s err=%s: %s",
                order_id,
                event,
                role,
                type(exc).__name__,
                exc,
            )
            return None

    def notificar_pedido_creado(self, snapshot: Optional[OrderNotificationSnapshot]) -> None:
        if snapshot is None:
            return
        if not self.client.is_configured:
            logger.warning(
                "Notificaciones por correo desactivadas para pedido #%s: falta CORREO_CENTRAL_API_KEY",
                snapshot.order_id,
            )
            return

        total_str = format_ars(snapshot.total)
        metodo_str = format_payment_method(snapshot.payment_method)
        items_lines = _format_items_lines(snapshot.items)
        detalle_prendas = "\n".join(items_lines) if items_lines else "(Detalle disponible en tu cuenta)"

        if snapshot.customer_email:
            lines = [
                f"Hola {snapshot.customer_name}, recibimos tu pedido en Showroom Isabella.",
                "",
                "Prendas:",
                detalle_prendas,
                "",
                f"Total: {total_str}",
                f"Método de pago: {metodo_str}",
                "Entrega: Retiro en el local",
                f"Dirección: {self.pickup_address}",
                "Coordiná el horario por WhatsApp cuando tu pedido esté listo.",
            ]
            if snapshot.payment_method == "transfer":
                lines.extend([
                    "",
                    "Para pagar, transferí al alias SHOWROOMISABELLAA indicando tu número de pedido y enviá el comprobante por WhatsApp.",
                ])
                wa_text = (
                    f"Hola! Hice la transferencia del pedido #{snapshot.order_id} "
                    f"en Showroom Isabella. Te envío el comprobante."
                )
                boton = {
                    "texto": "Enviar comprobante por WhatsApp",
                    "url": build_whatsapp_url(wa_text, self.whatsapp_number),
                }
            else:
                boton = {
                    "texto": "Ver mi pedido",
                    "url": f"{self.site_url}/orders/{snapshot.order_id}",
                }

            self._safe_send(
                role="cliente",
                event="creado",
                order_id=snapshot.order_id,
                to=snapshot.customer_email,
                subject=f"Recibimos tu pedido #{snapshot.order_id} - Showroom Isabella",
                titulo=f"Recibimos tu pedido #{snapshot.order_id}",
                mensaje="\n".join(lines),
                idempotency_key=f"showroomisabella-order-{snapshot.order_id}-created-client",
                boton=boton,
            )

        owner_to = self.owner_email
        if owner_to:
            owner_lines = [
                f"Ingresó un nuevo pedido en Showroom Isabella.",
                "",
                f"Cliente: {snapshot.customer_name}",
                f"Teléfono: {snapshot.customer_phone or '-'}",
                f"Email: {snapshot.customer_email or '-'}",
                "",
                "Prendas:",
                detalle_prendas,
                "",
                f"Total: {total_str}",
                f"Método de pago: {metodo_str}",
                "Entrega: Retiro en el local",
            ]
            self._safe_send(
                role="duena",
                event="creado",
                order_id=snapshot.order_id,
                to=owner_to,
                subject=f"Nuevo pedido #{snapshot.order_id} - Showroom Isabella",
                titulo=f"Nuevo pedido #{snapshot.order_id}",
                mensaje="\n".join(owner_lines),
                idempotency_key=f"showroomisabella-order-{snapshot.order_id}-created-owner",
                boton={
                    "texto": "Ver pedidos",
                    "url": f"{self.site_url}/admin/orders",
                },
            )

    def notificar_pago_confirmado(self, snapshot: Optional[OrderNotificationSnapshot]) -> None:
        if snapshot is None or not snapshot.customer_email:
            return
        if not self.client.is_configured:
            logger.warning(
                "Notificaciones por correo desactivadas para pago de pedido #%s: falta CORREO_CENTRAL_API_KEY",
                snapshot.order_id,
            )
            return

        total_str = format_ars(snapshot.total)
        metodo_str = format_payment_method(snapshot.payment_method)
        items_lines = _format_items_lines(snapshot.items)
        lines = [
            f"Hola {snapshot.customer_name}, confirmamos el pago de tu pedido #{snapshot.order_id}.",
        ]
        if items_lines:
            lines.extend(["", "Prendas:", *items_lines])
        lines.extend([
            "",
            f"Total abonado: {total_str}",
            f"Método de pago: {metodo_str}",
            "Entrega: Retiro en el local",
            "",
            "Te avisaremos por este medio cuando tu pedido esté listo para retirar.",
        ])
        self._safe_send(
            role="cliente",
            event="pago_confirmado",
            order_id=snapshot.order_id,
            to=snapshot.customer_email,
            subject=f"Pago confirmado - Pedido #{snapshot.order_id} - Showroom Isabella",
            titulo=f"Confirmamos tu pago (#{snapshot.order_id})",
            mensaje="\n".join(lines),
            idempotency_key=f"showroomisabella-order-{snapshot.order_id}-paid-client",
            boton={
                "texto": "Ver mi pedido",
                "url": f"{self.site_url}/orders/{snapshot.order_id}",
            },
        )

    def notificar_listo_para_retirar(self, snapshot: Optional[OrderNotificationSnapshot]) -> None:
        if snapshot is None or not snapshot.customer_email:
            return
        if not self.client.is_configured:
            logger.warning(
                "Notificaciones por correo desactivadas para retiro de pedido #%s: falta CORREO_CENTRAL_API_KEY",
                snapshot.order_id,
            )
            return

        total_str = format_ars(snapshot.total)
        items_lines = _format_items_lines(snapshot.items)
        lines = [
            f"Hola {snapshot.customer_name}, tu pedido #{snapshot.order_id} ya está listo para retirar en el local.",
            f"Dirección: {self.pickup_address}",
        ]
        if items_lines:
            lines.extend(["", "Prendas:", *items_lines])
        lines.extend([
            "",
            f"Total: {total_str}",
            "Coordiná el horario por WhatsApp para pasar a retirarlo.",
        ])
        wa_text = f"Hola! Recibí el aviso de que mi pedido #{snapshot.order_id} está listo para retirar."
        self._safe_send(
            role="cliente",
            event="listo_retirar",
            order_id=snapshot.order_id,
            to=snapshot.customer_email,
            subject=f"Tu pedido #{snapshot.order_id} está listo para retirar - Showroom Isabella",
            titulo=f"¡Tu pedido #{snapshot.order_id} está listo para retirar!",
            mensaje="\n".join(lines),
            idempotency_key=f"showroomisabella-order-{snapshot.order_id}-ready-client",
            boton={
                "texto": "Coordinar retiro por WhatsApp",
                "url": build_whatsapp_url(wa_text, self.whatsapp_number),
            },
        )


notificaciones_service = NotificacionesService()
