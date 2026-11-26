# Checkout, retractación y revisión de accesibilidad

## Despliegue

Publicar el backend de `dev` para habilitar acceso privado por pedido, cambio de transferencia a Mercado Pago, cancelación con restitución de variantes y conciliación automática. El frontend de test no despliega ese backend: usa la API compartida existente.

No hay migración SQL ni cambios de modelos en esta entrega. Mantener `SECRET_KEY` fuerte y estable: los enlaces privados dependen de ella. No compartir tokens ni publicarlos en logs. Ver también `pagos-invitados.md`.

La verificación administrativa y las acciones del cliente bloquean y refrescan la fila del pedido. Una transferencia pagada, cancelada, con stock liberado o ya cambiada a Mercado Pago no puede verificarse como transferencia pendiente. Cancelar dos veces no repone stock ni notifica dos veces. El correo a la dueña es best-effort mediante correo-central.

La conciliación conserva el advisory lock en una conexión dedicada y recorre pendientes por lotes de 100, sin dejar sin revisar los posteriores al primer lote. No depende de que la clienta mantenga abierta la pantalla. Si PayAlert devuelve `pending`, no se inventa una aprobación. No se tocó E:/payalert ni el pedido #9.

## Validación automatizada

- Pytest: 197 aprobados y 4 fallos; los mismos 4 fallan en una copia `git archive ad50c1e` anterior a estos cambios (171 aprobados). Sin worktrees ni acceso de escritura a la base compartida.
- Fallos previos: token Firebase inválido (`test_auth_module`), dos escenarios de `test_integration_complete` y disponibilidad de datos maestros (`test_master_data_module`).
- Vitest: 59/59 aprobados. Build `npm run build:test`: aprobado.
- En esta máquina esbuild agotó memoria en una repetición. Se repitieron Vitest y build con `GOMAXPROCS=2`, un solo worker de Vitest, sin modificar configuración del proyecto.
- Gate: `python C:/Users/PC-ASUS/.agents/quality-gate/gate.py --changed`.

## QA de navegador

Capturas y mediciones: `C:/Users/PC-ASUS/AppData/Local/hermes/profiles/ingeniero/cache/scratch/qa-isabella/checkout/`.

Se prueba el frontend publicado con autenticación simulada solamente en memoria del navegador y carrito local de una variante existente. Se bloquean escrituras de pedidos, pagos y clientes; no se pulsa confirmar ni se crea un pedido. El flujo posterior al pedido se verifica con pytest/Vitest y mocks.

En 360, 390 y 1366 px: un solo CTA de contacto a pago, sin `Continuar a entrega`, foco en el título al avanzar y regresar, sin desbordamiento horizontal y selección libre transferencia → Mercado Pago → transferencia. Con movimiento reducido no se usa scroll suave. Los controles principales del checkout miden al menos 44 px.

Contraste sobre blanco: cuerpo/etiquetas `#4b5563` = 7,56:1; monto y CTA de transferencia `#15803d` = 5,02:1. Se corrigió también el token Tailwind `body-text`, que conservaba 4,42:1 aunque la variable CSS global ya estaba corregida.

## Datos a revisar por la dueña (sin modificar la base)

Consulta pública de productos compartidos:

- #14 `POLLERA ASIMETRICA`: categoría `SHOE` (ahora etiqueta visible «Calzado»). Revisar asignación a polleras.
- #15 `POLLERA STRASS`: categoría `SHOE`. Revisar asignación a polleras.
- #12 `SHORT BEIGE RIGIDO`: categoría nula. Revisar asignación a shorts.

Los identificadores y categorías de la base no fueron editados. La traducción de presentación no corrige esas asignaciones.

Pendientes por decisión explícita: ISA-006 (precios de prueba) e ISA-011 (buscador). No se autoriza ni ejecuta publicación en `pro`, despliegue de backend ni migración remota.
