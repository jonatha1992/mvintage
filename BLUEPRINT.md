# BLUEPRINT

## Estado

- Rama de trabajo: `dev`.
- Marca pública: Showroom Isabella.
- Instagram oficial: @showroomisabella_ (https://www.instagram.com/showroomisabella_).
- Metadatos: archivo raíz `VERSION` y `frontend/public/version.json`.
- Checkout: contacto, retiro local y pago.
- API de pedidos: solo acepta `delivery_method="retiro_local"`; ausencia u otra modalidad responde 422.
- Administración logística histórica: conservada fuera del flujo público.
- Tests backend: fixtures SQLite en memoria; ninguna conexión a `.env` o base externa.
- Frontend build: `npm run build:test` funcionando exitosamente tras resolver tipos TS en `AdminViewProduct.vue` y `CollectionView.vue`.

## Decisiones

- Modalidad explícita: el modelo no asigna envío por defecto.
- Sin dirección ni cotización en checkout porque no existe entrega a domicilio.
- Efectivo significa pago al retirar.
- Identificadores técnicos existentes de Firebase, dominios y correos no se renombran sin infraestructura aprobada.

- Cuotas máximas por producto (`Product.max_installments`, 1/3/6/12, default 3; migración `add_product_max_installments`); `order_max_installments` en `backend/app/services/payment_installments.py` = mínimo del pedido. Aún sin integrar a Mercado Pago/PayAlert.

## Pendiente

- Proveer paquetes Python offline o habilitar conectividad a PyPI para instalar `sqlmodel` en `backend/.venv` (red aislada WinError 10061) y correr pytest.
- Proveer variables de entorno Firebase (`VITE_AUTH_DOMAIN`, `VITE_PROJECT_ID`, `VITE_STORAGE_BUCKET`, `VITE_MESSAGING_SENDER_ID`, `VITE_APP_ID`, `VITE_API_KEY`) requeridas para que el preview del frontend no falle al inicializar en blanco.
- Verificar integración Firebase, MercadoPago y email solo con credenciales/servicios reales autorizados.
- Validar capturas autenticadas del checkout a 390 y 1366 px cuando exista entorno local funcional.
