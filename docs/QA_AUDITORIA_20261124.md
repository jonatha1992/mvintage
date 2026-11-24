# Auditoría QA — Showroom Isabella — 24/11/2026

## Estado de entrega

Código corregido en `dev`. **Publicación Firebase test bloqueada por credenciales vencidas del desplegador**. El push de promoción a `test` se realizó, pero el sitio público todavía sirve el bundle previo (`index-DCRNM_h4.js`). No se reinició el backend del servidor ni se modificó la rama `pro`.

Commit de implementación: `71efe4e`. Promoción inicial a test: `76bc49d`.

## Hallazgos y evidencia

Las rutas de código son relativas a este repositorio. Evidencias locales: `C:/Users/PC-ASUS/AppData/Local/hermes/profiles/ingeniero/cache/scratch/qa-isabella/fix/`.

| ID | Corrección | Archivo:línea | Evidencia |
|---|---|---|---|
| 39236 | Link del carrito usa id y nombre codificado, respetando `/product/:id/:name?`. Búsqueda del resto de links: ProductCard ya usaba id. | `frontend/src/components/cart/ShoppingCart.vue:36` | `QaFixes.spec.ts`; `local/{390,1366}-39236-carrito.png` y `-carrito-navegado.png` |
| 39237 | POST real; validación nombre 2–100, email hasta 254, mensaje 10–4000, campos extra rechazados; límite 3/600 s por IP con limitador existente; correo-central a dueña, reply-to y email en cuerpo; errores 502/503 sin falso éxito. Frontend required, límites, espera, éxito/error, bloqueo de duplicados y WhatsApp; método POST sin PII en query string. | `backend/app/routes/contact.py:15,27`; `backend/app/main.py:91`; `frontend/src/views/shared/ContactView.vue:43,87` | `backend/tests/test_contact.py`; `ContactView.spec.ts`; `local/{390,1366}-39237-contacto-{exito,error}-mock.png`. Respuestas de navegador interceptadas deliberadamente: no se envió correo real ni se usó el backend remoto nuevo. |
| 39238 | Causa de datos: productos tenían categoria REMERA/CONJUNTO como texto, pero faltaban filas maestras. Se agregaron ambas categorías activas y se reclasificó el conjunto. Filtros no eran hardcodeados. | Tabla `category`, IDs 24 y 25; `product`, ID 5 | `db-before.txt`, `fix/db-update-final.txt`, `fix/db-after.txt`; captura local de categorías en ambas resoluciones; SELECT persistido y API real. |
| 39239 | Panel nativo dialog: categoría, precio, orden y limpiar, controles de 48px; foco modal, cierre Escape y restauración al botón. | `frontend/src/views/products/CollectionView.vue:193,256` | `QaFixes.spec.ts`; `local/390-39239-filtros.png`, `local/1366-39239-filtros-desktop.png`; navegador selecciona y limpia todos los filtros. |
| 39240 | Ayuda condicional a compras y Mercado Pago; catálogo explica WhatsApp; Mercado Pago solo visible si ambos flags están activos; retiro sin envíos. | `frontend/src/views/shared/HowToShopView.vue:7`; `ShippingView.vue:27` | `PurchaseHelp.spec.ts`: las cuatro combinaciones; `local/{390,1366}-39240-{como-comprar,retiro}.png`. Build test local tiene ambos flags activos, sin modificar configuración del negocio. |
| 39241 | Catch-all español y vuelta a tienda, noindex; producto inexistente no carga eternamente; carrito/menú/variantes/cantidad 48px; nombres accesibles y navegación en español; HTML es-AR; cantidad entera limitada al stock de variante y guarda de agregado; cabeceras API y Hosting. Guía de talles ya estaba en español y con categorías actuales. | `frontend/src/router.ts:37`; `views/shared/NotFoundView.vue:1`; `components/layout/Navbar.vue:124`; `components/cart/CartModal.vue:18`; `components/products/ProductDetail.vue:119,146,167,509,586`; `frontend/index.html:2`; `backend/app/main.py:68`; `frontend/firebase.json:11,34` | `test_contact.py` valida cabeceras JSON en 200 y 404; `QaFixes.spec.ts` cantidad 99 y fracción; `local/{390,1366}-39241-{404,talles,producto-stock-tactil}.png`; cajas táctiles medidas, stock real 5, input 9999 termina en 5. |

## Base compartida

Backup previo verificado en el servidor: `D:/Backups/showroomisabella/pre_qa_fix_20261124.dump`, **42.133 bytes**.

SQL ejecutado desde scratch: `qa-isabella-before.sql`, `qa-isabella-fix.sql`. Salidas completas antes/después en `qa-isabella/db-before.txt`, `qa-isabella/fix/db-update.txt`, `db-update-final.txt`, `db-after.txt`.

| Registro | Antes | Después |
|---|---|---|
| product 1 nombre | Top Isabella Clasico | Top Isabella Clásico |
| product 1 descripción | Top entallado con diseno moderno y calce comodo para uso diario. | Top entallado con diseño moderno y calce comodo para uso diario. |
| product 10 nombre | Moscúlosa con encaje (con espacio final) | Musculosa con encaje |
| product 5 categoria | VESTIDO | CONJUNTO |
| product 5 descripción | Vestido estilizado confeccionado con terminaciones finas. | Conjunto estilizado confeccionado con terminaciones finas. |
| category REMERA | inexistente | id 24, activa |
| category CONJUNTO | inexistente | id 25, activa |

La primera ejecución no actualizó dos nombres por espacios finales almacenados; la segunda usó `btrim` y verificó las condiciones antes de COMMIT. Las transacciones compararon todos los campos no editables de los 11 productos y todas las 26 variantes: sin cambios. No se ejecutaron escrituras de stock, precio ni fotos.

## Pruebas

- Backend completo: **140 passed, 5 failed**. Los cinco fallos coinciden con el baseline informado: token Firebase inválido; setup completo de tienda; inventory low stock; seed de maestros; update product. Sin fallos nuevos. Ocho tests nuevos de contacto/cabeceras pasan.
- Vitest: **15 passed**, cinco archivos. Incluye dos tests de contacto, tres de regresión, cuatro combinaciones de flags y seis tests existentes.
- `npm run build:test`: OK.
- `python C:/Users/PC-ASUS/.agents/quality-gate/gate.py --changed`: exit 0.
- Chromium real sobre build local a 390 y 1366: **22 comprobaciones/capturas**, sin overflow, sin errores JS ni imágenes rotas. Datos y fotos reales, contacto interceptado. Para consumir la API desde el preview local, ese navegador local usó `--disable-web-security`; no es evidencia de CORS/Hosting público.
- `fix/verify.py`, `fix/local/browser-results.json`, `backend-pytest.txt`, `vitest.txt`, `build-test.txt` conservan resultados reproducibles.

## Publicación pendiente

El desplegador registró `tests_ok` para test y luego `failed` en preview. Build remoto probado OK. Firebase devuelve `Authentication Error: Your credentials are no longer valid. Please run firebase login --reauth` para la cuenta configurada. Reintento de solo hosting:test confirmó la causa. No hay cuenta autorizada en Firebase CLI local ni login guardado en vault; se canceló el intento OAuth sin pedir contraseñas ni cerrar el navegador del usuario.

Control Apps **39250**: reautenticar Firebase del desplegador y reintentar publicación. No se cerraron como desplegados los hallazgos 39236–39241. Falta verificar el nuevo frontend en `https://showroomisabella-ar-test.web.app` a ambas resoluciones y sus headers Hosting; falta reinicio backend autorizado por el usuario para contacto/cabeceras remotos. El correo real no fue enviado en QA.
