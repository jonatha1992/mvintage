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

- Cuotas máximas por producto (`Product.max_installments`, 1/3, default 3; migración `add_product_max_installments`); `order_max_installments` en `backend/app/services/payment_installments.py` = mínimo del pedido, con techo de 3 incluso para datos históricos de 6/12. Aún sin integrar a Mercado Pago/PayAlert.
- Alias de transferencia por defecto: `SHOWROOMISABELLAA`; titular: Priscila Moyano. Sin cambios de datos desde el código de esta entrega.
- Imágenes (Control Apps 38734): `POST /api/v1/admin/images/upload` exige usuario admin/manager, archivo `image/*` de hasta 15 MiB y carpeta `productos` o `productos/originals`. Reenvía el archivo temporal sin cargarlo completo en RAM a `/v1/showroomisabella/upload`; `IMG_SERVER_URL` y `IMG_SERVER_API_KEY` son exclusivas del backend. No hay borrado remoto de imágenes en el frontend, por eso no se agregó DELETE.
- El cliente conserva WebP de 800 px y respaldo original; usa `apiClient` con token Firebase y deja que el navegador genere el boundary multipart. La configuración Vite usa accesos estáticos: un acceso dinámico a `import.meta.env[name]` incluía todas las variables VITE y filtraba la clave aunque ya no se usara explícitamente.
- Validación local de 38734: pytest base `113 passed / 5 failed`; con las pruebas nuevas `132 passed / 5 failed` (mismos cinco preexistentes). Build test y comparación binaria de dist contra la clave de `.env.test`: `ausente`. No se imprimen valores de credenciales.
- Separación de responsabilidades: autorización reutilizada de `core/security.py`, proxy y validación en `routes/admin_images.py`, transporte autenticado reutilizado del frontend. Sin nuevas consultas de catálogo ni procesamiento de imágenes en backend. No se midieron apertura/heap de navegador antes/después; queda pendiente ese gate de rendimiento y la prueba integrada contra el img-server real, no invocado en tests.
- Rotación manual (repositorio `E:/img-server`, solo lectura): sustituir `API_KEY_SHOWROOMISABELLA` en el entorno del img-server y reiniciarlo; actualizar `IMG_SERVER_API_KEY` del backend al mismo valor y reiniciar el backend. No existe endpoint de rotación; no se ejecutó ninguna rotación. El img-server actual limita archivos a 10 MiB, aunque el proxy permite 15 MiB.
- Correos transaccionales (pedidos, bienvenida y verificación de email): unificados en `correo-central` (`CorreoCentralClient`, plantillas `aviso`, `bienvenida`, `codigo`). Se eliminó `backend/app/core/mailer.py` y las variables SMTP de `config.py`.

## Pendiente

- Proveer paquetes Python offline o habilitar conectividad a PyPI para instalar `sqlmodel` en `backend/.venv` (red aislada WinError 10061) y correr pytest.
- Proveer variables de entorno Firebase (`VITE_AUTH_DOMAIN`, `VITE_PROJECT_ID`, `VITE_STORAGE_BUCKET`, `VITE_MESSAGING_SENDER_ID`, `VITE_APP_ID`, `VITE_API_KEY`) requeridas para que el preview del frontend no falle al inicializar en blanco.
- Verificar integración Firebase, MercadoPago y email solo con credenciales/servicios reales autorizados.
- Validar capturas autenticadas del checkout a 390 y 1366 px cuando exista entorno local funcional.
