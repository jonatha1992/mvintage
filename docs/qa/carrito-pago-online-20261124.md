# Carrito y pago online — 0.1.2

## Validación local

- Vitest: `Test Files 9 passed (9)` / `Tests 40 passed (40)`.
- `npm run build:test`: OK, TypeScript y Vite 7.1.2, 1060 módulos, sin dependencias nuevas.
- `uv run pytest -q --tb=short`: `5 failed, 154 passed` frente a baseline `5 failed, 140 passed`. Los fallos siguen siendo auth/token inválido, integración/maestros vacíos, integración/DateTime SQLite, maestros disponibles y actualización de producto/variantes.
- Nuevas pruebas backend: 7 de política de pago y 7 de payload/fallback PayAlert. No llaman servicios externos; SQLite en memoria.
- Solo se publica hosting test por el desplegador. No se actualizan backend remoto, base ni producción.

## Responsabilidades y recursos

- Store del carrito valida cantidades/stock antes de modificar el carrito; el composable compartido administra aviso y temporizador único.
- Componente del aviso administra presentación accesible y acceso al modal del carrito. Usa Teleport y Popover manual (top layer, con fallback fixed); no toma el foco al abrir. Pausa al recibir hover/foco; cierra a los tres segundos de inactividad.
- Badge usa el identificador de incorporación para repetir pop incluso cuando se reemplaza la cantidad por el mismo valor. CSS existente de 280 ms respeta reduced motion.
- Rutas validan métodos nuevos; modelos conservan `cash` para leer históricos. Consultas de transferencias reconocen el identificador histórico y el canónico.
- Controlador prepara título/descripción mediante un join acotado a los ítems del pedido; cliente HTTP inyectable serializa y aplica un único fallback ante `400 invalid_request`. No agrega carga completa de base ni dependencia.
- No se refactoriza el resto de logística histórica ni los componentes de administración fuera de los controles afectados.
- Baseline de navegador en `cache/scratch/qa-isabella/linea_base.json`; medición posterior y capturas se conservan en esa misma carpeta tras publicar. Las filas de base no se miden: no se accede a la base real.

## Límites

- Un PayAlert viejo que rechace los campos nuevos recibe un segundo intento sin ellos; durante ese fallback no puede garantizarse la exclusión de efectivo. Debe actualizarse PayAlert para aplicar `excludeCash`.
- Backend pendiente de publicación manual por el dueño. Hasta entonces el servidor no aplica aún la validación nueva.
- El texto `Efectivo` permanece exclusivamente como label de pedidos históricos (admin, estado del pedido y servicio de correo); no es una opción de compra.
