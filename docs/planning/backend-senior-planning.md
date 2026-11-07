# Planning Especializado - Senior Backend Developer (Python/FastAPI)

## Objetivo General
Implementar sistema completo de seguimiento de envíos, optimizar APIs existentes y crear funcionalidades administrativas avanzadas para M-Vintage.

## Contexto Técnico
- **Stack**: FastAPI + SQLModel + PostgreSQL + Alembic + Firebase Auth + MercadoPago
- **Arquitectura**: Controllers + Routes + Models + Services + Integrations
- **Base actual**: Sistema de pedidos funcional, autenticación, pagos con MercadoPago

---

## 🚀 SPRINT 1: Fundamentos del Sistema de Tracking (2 semanas - 80 horas)

### **Objetivo Sprint 1**
Crear la base del sistema de seguimiento con modelos actualizados, APIs administrativas básicas y endpoints para gestión de envíos.

### **Tareas Principales**

#### **T1.1: Actualización de Modelos de Base de Datos** ⏱️ 12 horas
**Prioridad**: CRÍTICA | **Complejidad**: Media

**Descripción**: Extender modelo Order con campos de tracking y crear esquemas de validación.

**Subtareas**:
- Actualizar `backend/app/models/order.py` con nuevos campos:
  - `tracking_number: Optional[str]` (VARCHAR 255)
  - `shipping_provider: Optional[str]` (VARCHAR 100) 
  - `shipped_at: Optional[datetime]`
  - `estimated_delivery: Optional[datetime]`
  - `shipped_by: Optional[int]` (foreign key to users)
- Crear `backend/app/schemas/shipping_schemas.py` con DTOs:
  - `ShippingUpdate`, `TrackingInfo`, `ShippingResponse`
- Generar migración Alembic: `alembic revision --autogenerate -m "add shipping tracking fields"`

**Criterios de Aceptación**:
- ✅ Migración ejecuta sin errores en dev/test
- ✅ Nuevos campos tienen validaciones apropiadas
- ✅ Esquemas Pydantic validan correctamente formatos de tracking
- ✅ Tests unitarios para nuevos modelos pasan

**Dependencias**: Ninguna  
**Entregables**: Migración SQL, modelos actualizados, esquemas validados

---

#### **T1.2: APIs Administrativas de Gestión de Envíos** ⏱️ 20 horas
**Prioridad**: CRÍTICA | **Complejidad**: Alta

**Descripción**: Crear endpoints administrativos para gestión completa del ciclo de envíos.

**Subtareas**:
- Crear `backend/app/routes/admin_shipping.py` con endpoints:
  - `GET /api/v1/admin/orders?status=pending_shipment` - Pedidos listos para envío
  - `PUT /api/v1/admin/orders/{id}/shipping` - Actualizar info de envío  
  - `POST /api/v1/admin/orders/{id}/mark-shipped` - Marcar como enviado
  - `GET /api/v1/admin/orders/shipping-stats` - KPIs de envíos
- Implementar `backend/app/controllers/shipping_controller.py` con lógica:
  - `update_shipping_info()`, `mark_as_shipped()`, `get_shipping_stats()`
- Validaciones de permisos (solo admin/manager)
- Logging detallado de cambios de estado

**Criterios de Aceptación**:
- ✅ Solo usuarios admin/manager pueden acceder a endpoints
- ✅ Validación de formatos de tracking (alfanumérico, 8-30 caracteres)
- ✅ Audit trail: quién marcó como enviado y cuándo
- ✅ Response incluye tracking_url generada automáticamente
- ✅ Manejo de errores con códigos HTTP apropiados

**Dependencias**: T1.1 (modelos actualizados)  
**Entregables**: 4 endpoints funcionales, controller con lógica de negocio

---

#### **T1.3: Endpoints Cliente para Consulta de Envíos** ⏱️ 16 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: APIs para que clientes consulten estado de sus envíos desde frontend.

**Subtareas**:
- Crear `backend/app/routes/customer_orders.py` con endpoints:
  - `GET /api/v1/orders/{id}/tracking` - Info de tracking para orden específica
  - `GET /api/v1/orders/my-orders?include_tracking=true` - Listado con tracking
- Implementar lógica en `order_controller.py`:
  - `get_order_tracking()`, `get_user_orders_with_tracking()`
- Response con tracking_url, provider_name, status_description
- Validación de ownership (usuario solo ve sus pedidos)

**Criterios de Aceptación**:
- ✅ Usuario autenticado solo accede a sus propios pedidos
- ✅ Response incluye tracking_url funcional para cada proveedor
- ✅ Campo status_description amigable ("En preparación", "Enviado", etc.)
- ✅ Filtros opcionales por estado de envío
- ✅ Paginación para usuarios con muchos pedidos

**Dependencias**: T1.1, T1.2  
**Entregables**: 2 endpoints cliente, lógica de ownership validation

---

#### **T1.4: Notificaciones por Email de Envíos** ⏱️ 14 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Sistema automático de emails cuando pedido es marcado como enviado.

**Subtareas**:
- Extender `backend/app/services/email_service.py` con:
  - `send_shipping_notification()`, template HTML para tracking
- Crear template `shipping_notification.html` con:
  - Número de pedido, tracking number, enlaces de seguimiento
  - Información de contacto/soporte claramente visible
- Integrar con endpoint `mark-shipped` para envío automático
- Configurar queue asíncrona para emails (opcional: Celery)

**Criterios de Aceptación**:
- ✅ Email enviado automáticamente al marcar como enviado
- ✅ Template responsive que se ve bien en móvil/desktop
- ✅ Enlaces de tracking funcionales por proveedor
- ✅ Fallback si envío de email falla (no bloquea mark-shipped)
- ✅ Log de emails enviados con timestamp

**Dependencias**: T1.2 (mark-shipped endpoint)  
**Entregables**: Template email, servicio de notificaciones automáticas

---

#### **T1.5: Testing y Validación Sprint 1** ⏱️ 18 horas
**Prioridad**: CRÍTICA | **Complejidad**: Media

**Descripción**: Cobertura completa de testing para nuevas funcionalidades.

**Subtareas**:
- Crear `backend/tests/test_shipping_module.py` con:
  - Tests de modelos (validaciones, constraints)
  - Tests de endpoints admin (permisos, validaciones)
  - Tests de endpoints cliente (ownership, responses)
  - Tests de emails (envío, templates)
- Integration tests para flujo completo:
  - Crear pedido → admin carga tracking → cliente consulta → email enviado
- Performance tests para endpoints con grandes volúmenes
- Documentar casos edge (tracking duplicado, pedido inexistente)

**Criterios de Aceptación**:
- ✅ Cobertura de tests >90% para código nuevo
- ✅ Tests de integración cubren flujo end-to-end
- ✅ Tests de permisos validan acceso apropiado
- ✅ Performance tests validan <200ms response time promedio
- ✅ Documentación de testing actualizada

**Dependencias**: T1.1, T1.2, T1.3, T1.4  
**Entregables**: Suite completa de tests, reporte de cobertura

---

### **Definition of Done Sprint 1**
- [ ] Migración de BD ejecutada exitosamente en test/staging
- [ ] 6 endpoints nuevos documentados en Swagger (/docs)
- [ ] Tests unitarios e integración pasan al 100%
- [ ] Email de tracking enviado automáticamente y validado
- [ ] Métricas de performance dentro de SLA (<200ms)
- [ ] Code review completado y aprobado
- [ ] Deployment a staging exitoso

---

## 🔧 SPRINT 2: Integraciones Externas y Automatización (3 semanas - 120 horas)

### **Objetivo Sprint 2**
Integrar APIs de proveedores de envío, automatizar actualización de estados y crear sistema robusto de notificaciones.

### **Tareas Principales**

#### **T2.1: Integración API Correo Argentino** ⏱️ 24 horas
**Prioridad**: ALTA | **Complejidad**: Alta

**Descripción**: Conectar con API oficial de Correo Argentino para tracking automático.

**Subtareas**:
- Investigar y documentar API de Correo Argentino (endpoints, auth, rate limits)
- Crear `backend/app/integrations/correo_argentino.py`:
  - Clase `CorreoArgentinoClient` con métodos de tracking
  - `get_tracking_status()`, `validate_tracking_number()`
  - Rate limiting y retry logic para API externa
- Configurar credenciales en environment variables
- Cache de respuestas (Redis opcional) para evitar llamadas repetidas

**Criterios de Aceptación**:
- ✅ Integración maneja todos los estados posibles de tracking
- ✅ Rate limiting respeta límites de API externa
- ✅ Errores de API externa no rompen funcionamiento interno
- ✅ Cache reduce llamadas duplicadas en 80%
- ✅ Logs estructurados para debugging de API calls

**Dependencias**: Sprint 1 completado  
**Entregables**: Cliente de API funcional, documentación de integración

---

#### **T2.2: Integración Multi-Proveedor (OCA, Andreani)** ⏱️ 28 horas
**Prioridad**: MEDIA | **Complejidad**: Alta

**Descripción**: Ampliar integraciones a múltiples proveedores con patrón unificado.

**Subtareas**:
- Crear `backend/app/integrations/base_shipping_provider.py`:
  - Abstract class con interface común para todos los proveedores
- Implementar `oca_client.py` y `andreani_client.py` siguiendo interface
- Factory pattern para instanciar provider apropiado
- Unified response format independiente del proveedor
- Configuration management para habilitar/deshabilitar providers

**Criterios de Aceptación**:
- ✅ Interface común permite agregar nuevos proveedores fácilmente
- ✅ Response normalizada independiente del proveedor
- ✅ Configuración permite habilitar providers por environment
- ✅ Fallback graceful si proveedor no está disponible
- ✅ Métricas de performance por proveedor

**Dependencias**: T2.1 (patrón establecido)  
**Entregables**: 3 providers integrados, factory pattern implementado

---

#### **T2.3: Automatización de Actualización de Estados** ⏱️ 22 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Job automático que consulta APIs externas y actualiza estados internos.

**Subtareas**:
- Crear `backend/app/jobs/tracking_updater.py`:
  - Scheduled job (APScheduler) que consulta tracking cada 4 horas
  - Lógica para actualizar estado interno basado en respuesta de APIs
- Background task para procesamiento asíncrono
- Estado tracking: "shipped" → "in_transit" → "delivered" → "failed_delivery"
- Webhook receivers para notificaciones push de proveedores (si disponible)

**Criterios de Aceptación**:
- ✅ Job ejecuta automáticamente cada 4 horas sin intervención
- ✅ Actualiza solo pedidos en estado "shipped" o "in_transit"
- ✅ Maneja gracefully errores de APIs externas
- ✅ Log estructurado de todas las actualizaciones automáticas
- ✅ Configurable via environment variables

**Dependencias**: T2.1, T2.2 (integraciones funcionando)  
**Entregables**: Job scheduler, background tasks configurados

---

#### **T2.4: Sistema Avanzado de Notificaciones** ⏱️ 20 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: Notificaciones automáticas para cambios de estado de envío.

**Subtareas**:
- Extender `notification_service.py` con:
  - Emails para "shipped", "in_transit", "delivered", "delayed"
  - WhatsApp opcional (Twilio API) para tracking updates
  - Push notifications para web app (service workers)
- Template system con personalization (nombre cliente, tracking info)
- Preference management: usuario elige qué notificaciones recibir
- Rate limiting para evitar spam

**Criterios de Aceptación**:
- ✅ Emails automáticos para cada cambio de estado
- ✅ Templates personalizados por tipo de estado
- ✅ Usuario puede configurar preferencias de notificación
- ✅ Rate limiting previene envío excesivo
- ✅ Métricas de delivery rate por canal

**Dependencias**: T2.3 (estados automáticos)  
**Entregables**: 4 templates email, sistema de preferencias

---

#### **T2.5: Webhook Receivers y APIs Real-time** ⏱️ 16 horas
**Prioridad**: BAJA | **Complejidad**: Media

**Descripción**: Endpoints para recibir notificaciones push de proveedores de envío.

**Subtareas**:
- Crear `backend/app/routes/webhooks.py`:
  - Endpoints para recibir notificaciones de Correo Argentino, OCA, etc.
  - Validación de signatures para seguridad
- WebSocket endpoints para updates real-time en frontend
- Queue system para procesamiento asíncrono de webhooks
- Duplicate detection para evitar procesamiento múltiple

**Criterios de Aceptación**:
- ✅ Webhooks validan correctamente signatures de proveedores
- ✅ Updates real-time reflejados en frontend inmediatamente
- ✅ Queue previene perdida de webhooks en picos de tráfico
- ✅ Duplicate detection evita procesamiento múltiple
- ✅ Monitoring de webhook delivery rates

**Dependencias**: T2.1, T2.2, T2.3  
**Entregables**: Webhook endpoints seguros, WebSocket real-time

---

#### **T2.6: Testing e Integración Sprint 2** ⏱️ 30 horas
**Prioridad**: CRÍTICA | **Complejidad**: Alta

**Descripción**: Testing exhaustivo de integraciones externas y flujos automáticos.

**Subtareas**:
- Mocking de APIs externas para testing determinístico
- Integration tests para flujos multi-proveedor
- Load testing para scheduled jobs y webhook processing
- Error scenarios: API down, rate limiting, malformed responses
- End-to-end testing con sandbox/staging de proveedores

**Criterios de Aceptación**:
- ✅ Tests funcionan sin conexión a APIs externas (mocked)
- ✅ Load tests validan performance bajo 1000+ webhooks/min
- ✅ Error handling testado para todos los failure modes
- ✅ Integration tests con sandbox environments pasan
- ✅ Monitoring y alerting configurado para APIs externas

**Dependencias**: Todas las tareas T2.1-T2.5  
**Entregables**: Suite tests integraciones, mocks de APIs externas

---

### **Definition of Done Sprint 2**
- [ ] 3 proveedores de envío integrados y funcionando
- [ ] Jobs automáticos ejecutándose en staging sin errores
- [ ] Webhooks recibiendo y procesando notificaciones correctamente
- [ ] Sistema de notificaciones enviando emails automáticamente
- [ ] Load tests pasan con 1000+ tracking updates/hora
- [ ] Monitoring dashboard mostrando métricas de integración
- [ ] Documentación de APIs externas y troubleshooting

---

## ⚡ SPRINT 3: Performance y Optimización (2 semanas - 80 horas)

### **Objetivo Sprint 3**
Optimizar performance de APIs existentes, implementar caching estratégico y finalizar funcionalidades administrativas.

### **Tareas Principales**

#### **T3.1: Optimización de Performance de APIs** ⏱️ 24 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Mejorar tiempos de respuesta de APIs críticas y escalabilidad.

**Subtareas**:
- Profiling de APIs existentes para identificar bottlenecks
- Optimización de queries SQL con indexes estratégicos:
  - Index en `orders.customer_id` para my-orders
  - Composite index en `orders.status, created_at` para admin filters
- Implementar pagination inteligente con cursor-based pagination
- Database connection pooling optimization
- Response compression para endpoints que retornan grandes volúmenes

**Criterios de Aceptación**:
- ✅ APIs críticas responden <100ms en p95
- ✅ Endpoints con paginación manejan 10k+ records eficientemente
- ✅ Database queries optimizadas (no N+1 queries)
- ✅ Memory usage optimizado para payloads grandes
- ✅ Metrics dashboard muestra mejoras de performance

**Dependencias**: APIs estables de sprints anteriores  
**Entregables**: APIs optimizadas, métricas de performance mejoradas

---

#### **T3.2: Sistema de Caché Redis** ⏱️ 18 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: Implementar caching estratégico para reducir carga en BD y APIs externas.

**Subtareas**:
- Setup Redis en desarrollo y staging environments
- Implementar `backend/app/core/cache.py`:
  - Cache decorator para métodos frecuentemente llamados
  - Cache de responses de APIs externas (TTL 1 hora)
  - Cache de queries costosas de BD (user orders, product searches)
- Cache invalidation strategy para datos que cambian
- Metrics de cache hit rate y performance gains

**Criterios de Aceptación**:
- ✅ Cache hit rate >80% para endpoints frecuentes
- ✅ APIs externas cacheadas reducen calls en 90%
- ✅ Cache invalidation mantiene data consistency
- ✅ Redis failover no afecta funcionamiento (graceful degradation)
- ✅ Memory usage de Redis monitoreado y alertas configuradas

**Dependencias**: T3.1 (baseline de performance)  
**Entregables**: Redis configurado, cache strategy implementada

---

#### **T3.3: Dashboard Administrativo Avanzado** ⏱️ 20 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: APIs para dashboard admin con KPIs y reportes de envíos.

**Subtareas**:
- Crear `backend/app/routes/admin_analytics.py`:
  - `GET /admin/dashboard/shipping-stats` - KPIs de envíos
  - `GET /admin/dashboard/performance-metrics` - Métricas de performance
  - `GET /admin/reports/shipping-report` - Reporte detallado con filtros
- Implementar aggregations eficientes:
  - Orders by status, average shipping time, problem orders
  - Performance metrics by provider, error rates
- Export functionality para reportes (CSV, PDF)
- Real-time metrics con WebSocket updates

**Criterios de Aceptación**:
- ✅ Dashboard carga en <2 segundos con datos de último mes
- ✅ Reportes generan archivos CSV/PDF correctamente
- ✅ Metrics actualizadas en real-time sin polling excesivo
- ✅ Filtros permiten análisis granular por periodo/proveedor
- ✅ Mobile-responsive para acceso admin desde móvil

**Dependencias**: Datos históricos de sprints anteriores  
**Entregables**: 3 endpoints analytics, sistema de reportes

---

#### **T3.4: Monitoring y Alerting** ⏱️ 12 horas
**Prioridad**: ALTA | **Complejidad**: Baja

**Descripción**: Sistema de monitoreo y alertas para producción.

**Subtareas**:
- Implementar health checks para todos los servicios:
  - Database connectivity, Redis availability, External APIs status
- Structured logging con correlation IDs
- Error tracking y alerting:
  - Email alerts para API errors >5%
  - Slack notifications para tracking job failures
- Performance monitoring:
  - APM integration (opcional: New Relic, DataDog)
  - Custom metrics para business logic

**Criterios de Aceptación**:
- ✅ Health checks reportan status de todos los servicios
- ✅ Alerts enviadas automáticamente para problemas críticos
- ✅ Logs estructurados permiten debugging eficiente
- ✅ Correlation IDs facilitan tracing de requests
- ✅ Dashboard de monitoring accesible para equipo

**Dependencias**: Sistemas de sprints anteriores funcionando  
**Entregables**: Health checks, alerting configurado

---

#### **T3.5: Documentación y Handoff** ⏱️ 6 horas
**Prioridad**: MEDIA | **Complejidad**: Baja

**Descripción**: Documentación completa para mantenimiento y future development.

**Subtareas**:
- Actualizar Swagger/OpenAPI documentation
- Crear runbook para operaciones comunes:
  - Troubleshooting integraciones, restarting jobs, cache management
- Architecture documentation con diagramas actualizados
- Performance benchmarks y recommendations
- Security checklist y best practices

**Criterios de Aceptación**:
- ✅ Swagger docs 100% actualizadas con ejemplos
- ✅ Runbook cubre scenarios operacionales comunes
- ✅ Architecture diagrams reflejan estado actual
- ✅ Performance benchmarks documentados
- ✅ Security checklist verificada y completa

**Dependencias**: Todas las implementaciones anteriores  
**Entregables**: Documentación completa, runbooks operacionales

---

### **Definition of Done Sprint 3**
- [ ] APIs optimizadas con performance <100ms p95
- [ ] Redis cache implementado con >80% hit rate
- [ ] Dashboard admin funcionando con real-time updates
- [ ] Monitoring y alerting configurado y funcionando
- [ ] Documentación completa y actualizada
- [ ] Security checklist verificada
- [ ] Performance benchmarks establecidos

---

## 📋 Resumen de Entregables por Sprint

### Sprint 1 (2 semanas)
- ✅ 6 nuevos endpoints (4 admin + 2 cliente)
- ✅ Modelos de BD actualizados con migración
- ✅ Sistema de emails automáticos
- ✅ Tests unitarios e integración
- **Total**: 80 horas

### Sprint 2 (3 semanas)  
- ✅ 3 integraciones de proveedores de envío
- ✅ Jobs automáticos para tracking updates
- ✅ Sistema de notificaciones multi-canal
- ✅ Webhooks y real-time updates
- **Total**: 120 horas

### Sprint 3 (2 semanas)
- ✅ APIs optimizadas con caching Redis
- ✅ Dashboard administrativo avanzado
- ✅ Monitoring y alerting completo
- ✅ Documentación y handoff
- **Total**: 80 horas

## 🎯 Métricas de Éxito

### Performance
- Response time APIs <100ms (p95)
- Cache hit rate >80% 
- External API calls reducidas 90%

### Funcionalidad
- 100% pedidos con tracking automático
- 3 proveedores integrados y funcionando
- Emails automáticos con 99% delivery rate

### Calidad
- Test coverage >90% código nuevo
- Zero downtime deployments
- Error rate <1% para funcionalidades críticas

---

**TOTAL ESTIMADO**: 280 horas (7 semanas) para Senior Backend Developer

**Nota**: Este planning asume dedicación full-time al proyecto. Ajustar estimaciones según disponibilidad real del desarrollador.