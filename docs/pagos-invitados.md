# Acceso invitado y conciliación de Mercado Pago

- Desplegar backend y frontend del mismo cambio. No requiere SQL: los enlaces usan HMAC-SHA256 por pedido con `SECRET_KEY` del servidor. Mantener una clave secreta fuerte y estable; rotarla invalida enlaces existentes.
- El frontend guarda el token por pedido en localStorage. El retorno de PayAlert y los correos incluyen el enlace privado; no compartirlo. Un token de otro pedido devuelve 403.
- El mantenimiento automático consulta pagos pendientes de Mercado Pago creados dentro del TTL de 24 h, cada 2 minutos, antes de la limpieza de vencidos. Conserva el advisory lock en una conexión dedicada durante los commits. No depende de que la clienta vuelva al sitio.
- La pantalla de retorno consulta cada 5 segundos hasta 2 minutos. No anuncia pago confirmado ni vacía el carrito hasta que el servidor devuelva aprobado.
- No se agregaron webhooks ni se modificó PayAlert. Si PayAlert sigue devolviendo `pending` para el pedido #9, este cambio no puede convertirlo en aprobado: debe resolverse el estado en el proveedor. No se alteró ese pedido ni la base compartida.
- Los pedidos antiguos pueden recuperarse con un enlace generado por el backend; no generar enlaces reales ni mostrar tokens en logs públicos.
