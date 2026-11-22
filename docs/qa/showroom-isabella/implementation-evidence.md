# Showroom Isabella — evidencia de preparación

- Rama: `dev`, creada desde `origin/dev` tras `git fetch origin`; `dev` estaba 1 commit delante de `test` y no contenía commits exclusivos respecto de test en esa comparación. Árbol inicial limpio. No se hizo commit, push ni deploy.
- Base verificada: `test` en `93c5446821029e6a90368d6cf21949e4eaa58bf4`; `origin/dev` en `76a1267fc63ab64c0bdf0a867851d0b8957f35f7`.
- Implementación: marca pública Showroom Isabella; checkout de retiro local; API de pedidos exige `delivery_method="retiro_local"` y rechaza ausencia u otra modalidad con 422; correo y textos de tienda ajustados. Legado administrativo de logística queda preservado, fuera del flujo de compra.
- Regresiones agregadas: `backend/tests/test_order_pickup_policy.py` cubre retiro aceptado y envío/modalidad ausente rechazados. `backend/tests/conftest.py` usa SQLite en memoria para aislar la suite.
- Metadatos: `VERSION/version.json`; continuidad: `BLUEPRINT.md`; tareas de VS Code: `.vscode/launch.json` y `.vscode/tasks.json`.

## Verificaciones y bloqueos

- `python C:/Users/PC-ASUS/.agents/quality-gate/gate.py --changed`: pasó (exit 0).
- `graphify update .`: completó; grafo regenerado, 2551 nodos / 3932 aristas.
- `git diff --check`: pasó sin advertencias de espacios ni formato.
- `npm ci`: resuelto tras detener proceso local huérfano PID 8624/19692 (esbuild/vite preview en puerto 4177 dentro de mvintage). 995 paquetes instalados exitosamente.
- `npm run build:test`: exitoso (exit 0) tras corregir tipos en `AdminViewProduct.vue` y `CollectionView.vue`.
- `VERSION`: corregido directorio erróneo `VERSION/` a archivo raíz `VERSION` (0.1.0) y archivo público `frontend/public/version.json`.
- Instagram: actualizado en `Footer.vue`, `email_order_confirmation.html` y `email_verification.html` a `@showroomisabella_` (`https://www.instagram.com/showroomisabella_/`).
- Backend Python: entorno `.venv` creado con Python 3.13; instalación de `requirements.txt` intentada vía `uv pip install` y `pip install`, bloqueada por aislamiento de red (`WinError 10061` a files.pythonhosted.org:443). `pytest tests/test_order_pickup_policy.py` falla por ausencia de `sqlmodel` en el host.
- Diagnóstico de capturas previas en blanco: `frontend/src/config/firebase.ts` ejecuta `initializeApp(firebaseConfig)` sincrónicamente al importar; al faltar `VITE_PROJECT_ID` y `VITE_AUTH_DOMAIN` en `.env`, Firebase lanza excepción y aborta el render de la app en blanco antes de montar `#app`.
- No se realizaron commits, pushes ni deploys; baseline preservado.

## Log de delegación

El log completo de Codex y comandos previos quedó en el scratch del equipo: `C:/Users/PC-ASUS/AppData/Local/hermes/cache/scratch/mvintage-codex.log` y `C:/Users/PC-ASUS/AppData/Local/hermes/cache/scratch/codex_fix.log`. Codex reportó límite de cuota OpenAI (hit usage limit); los parches requeridos fueron aplicados directamente.
