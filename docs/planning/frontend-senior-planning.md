# Planning Especializado - Senior Frontend Developer (Vue 3/TypeScript)

## Objetivo General
Crear experiencia de usuario excepcional con dashboard personal, panel administrativo de envíos y optimizaciones de performance para M-Vintage.

## Contexto Técnico
- **Stack**: Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia + Vue Router
- **Estado actual**: ProductGrid optimizado, checkout funcional pero necesita simplificación
- **Integración**: APIs backend para tracking, Firebase Auth, MercadoPago frontend

---

## 🎨 SPRINT 1: Dashboard Usuario y Navegación (2 semanas - 80 horas)

### **Objetivo Sprint 1**
Crear experiencia post-compra excepcional con dashboard personal, navegación mejorada y integración completa del sistema de tracking.

### **Tareas Principales**

#### **T1.1: Reestructuración de Navegación Principal** ⏱️ 16 horas
**Prioridad**: CRÍTICA | **Complejidad**: Media

**Descripción**: Mejorar Navbar.vue con menú "Mi Cuenta" organizado y profesional.

**Subtareas**:
- Actualizar `frontend/src/components/layout/Navbar.vue`:
  - Agregar dropdown "Mi Cuenta" para usuarios autenticados
  - Links organizados: "Dashboard", "Mis Pedidos", "Mi Perfil", "Cerrar Sesión"
  - Badge de notificaciones para pedidos enviados
  - Remover "Cerrar Sesión" suelto del navbar principal
- Implementar estados activos y hover effects
- Mobile-responsive con hamburger menu mejorado
- Animaciones suaves con Tailwind transitions

**Criterios de Aceptación**:
- ✅ Dropdown se comporta correctamente en móvil y desktop
- ✅ Estados activos indican página actual claramente
- ✅ Badge de notificaciones actualiza automáticamente
- ✅ Animaciones fluidas sin lag en dispositivos lentos
- ✅ Accessibility compliance (ARIA labels, keyboard navigation)

**Dependencias**: Ninguna (mejora de componente existente)  
**Entregables**: Navbar.vue mejorado, sistema de notificaciones visuales

---

#### **T1.2: Dashboard Personal del Usuario** ⏱️ 20 horas
**Prioridad**: CRÍTICA | **Complejidad**: Alta

**Descripción**: Crear AccountDashboard.vue como hub principal del usuario autenticado.

**Subtareas**:
- Crear `frontend/src/views/account/AccountDashboard.vue`:
  - Overview de último pedido con estado actual
  - Accesos rápidos a "Mis Pedidos", "Mi Perfil", "Soporte"
  - Información de contacto/soporte visible y accesible
  - Diseño que inspire confianza y profesionalismo
- Implementar `frontend/src/composables/useAccountDashboard.ts`:
  - Lógica para cargar datos del usuario
  - Estado de último pedido, estadísticas básicas
- Configurar ruta `/account/dashboard` con auth guard
- Responsive design optimizado para mobile-first

**Criterios de Aceptación**:
- ✅ Dashboard carga en <2 segundos con datos del usuario
- ✅ Último pedido muestra estado actual con diseño claro
- ✅ Información de soporte fácilmente accesible
- ✅ Design system consistente con resto de la aplicación
- ✅ Mobile experience tan buena como desktop

**Dependencias**: APIs backend funcionando (GET user orders)  
**Entregables**: AccountDashboard.vue, composable de lógica, ruta configurada

---

#### **T1.3: Integración Completa de Sistema de Tracking** ⏱️ 18 horas
**Prioridad**: ALTA | **Complejidad**: Alta

**Descripción**: Conectar frontend con APIs de tracking backend para mostrar estado de envíos.

**Subtareas**:
- Actualizar `frontend/src/types/orders.ts` con nuevos campos:
  - `tracking_number`, `shipping_provider`, `shipped_at`, `tracking_url`
- Crear `frontend/src/services/trackingService.ts`:
  - `getOrderTracking()`, `getTrackingHistory()`, `refreshTrackingStatus()`
- Extender `frontend/src/store/orders.ts` (Pinia):
  - Estado para tracking info, acciones para fetch/update
- Implementar error handling para APIs externas no disponibles

**Criterios de Aceptación**:
- ✅ Types TypeScript cubren todos los campos de tracking
- ✅ Service maneja correctly errores de APIs externas
- ✅ Store mantiene estado sincronizado automáticamente
- ✅ Loading states durante llamadas a tracking APIs
- ✅ Fallback graceful si tracking no está disponible

**Dependencias**: CRÍTICA - Backend APIs de tracking funcionando (Sprint 1 Backend)  
**Entregables**: Services de tracking, types actualizados, store mejorado

---

#### **T1.4: Mejora de OrderDetailView.vue** ⏱️ 14 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Timeline visual de estados y sección destacada de tracking.

**Subtareas**:
- Rediseñar `frontend/src/views/orders/OrderDetailView.vue`:
  - Timeline visual: Confirmado → Pagado → Enviado → Entregado
  - Sección destacada con tracking number cuando esté disponible
  - Enlaces directos a páginas de seguimiento (Correo, OCA, Andreani)
  - Botón "Copiar tracking" con feedback visual
- Crear componente `TrackingTimeline.vue` reutilizable:
  - Estados con iconos y colores diferenciados
  - Animaciones de progreso entre estados
- Información de soporte: WhatsApp, email claramente visible
- Copy-to-clipboard functionality con toast notifications

**Criterios de Aceptación**:
- ✅ Timeline refleja correctamente estado actual del pedido
- ✅ Enlaces de tracking abren en nueva pestaña y funcionan
- ✅ Botón copiar tracking funciona en todos los browsers
- ✅ Información de soporte siempre visible y accesible
- ✅ Loading states para cuando se está cargando tracking

**Dependencias**: T1.3 (integración tracking) + Backend tracking APIs  
**Entregables**: OrderDetailView rediseñado, TrackingTimeline component

---

#### **T1.5: Flujo Post-Compra Optimizado** ⏱️ 12 horas
**Prioridad**: MEDIA | **Complejidad**: Baja

**Descripción**: Redirigir usuarios a ver su pedido inmediatamente después de comprar.

**Subtareas**:
- Modificar `frontend/src/views/checkout/CheckoutView.vue`:
  - Redirección a `/orders/{id}` después de pago exitoso
  - En lugar de ir a home, mostrar inmediatamente el pedido creado
  - Mensaje de éxito con información clara sobre próximos pasos
- Crear página de éxito intermedia (opcional):
  - Confirmación visual de compra exitosa
  - Enlace destacado al pedido recién creado
  - Información sobre tiempo estimado de procesamiento

**Criterios de Aceptación**:
- ✅ Usuario ve su pedido inmediatamente después de pagar
- ✅ Mensaje de éxito incluye información útil y clara
- ✅ No hay confusión sobre qué pasó después del pago
- ✅ Enlace al pedido funciona correctamente
- ✅ Back button no rompe el flujo

**Dependencias**: T1.4 (OrderDetail mejorado)  
**Entregables**: CheckoutView modificado, flujo post-compra optimizado

---

### **Definition of Done Sprint 1**
- [ ] Navegación con menú "Mi Cuenta" funcionando en móvil/desktop
- [ ] Dashboard personal carga datos del usuario correctamente
- [ ] Tracking integration muestra estado de envíos real-time
- [ ] OrderDetail con timeline visual y enlaces de tracking funcionales
- [ ] Flujo post-compra redirige a pedido recién creado
- [ ] Tests de componentes pasan y TypeScript compila sin errores
- [ ] Cross-browser testing completado (Chrome, Firefox, Safari, Edge)

---

## 🛠️ SPRINT 2: Panel Admin y Optimización UX (3 semanas - 120 horas)

### **Objetivo Sprint 2**
Crear panel administrativo completo para gestión de envíos, simplificar checkout y optimizar componentes existentes.

### **Tareas Principales**

#### **T2.1: Panel Administrativo de Gestión de Envíos** ⏱️ 32 horas
**Prioridad**: CRÍTICA | **Complejidad**: Alta

**Descripción**: Vista principal admin para gestionar todos los envíos de pedidos.

**Subtareas**:
- Crear `frontend/src/views/admin/AdminShippingView.vue`:
  - Vista principal con filtros por estado de envío
  - Filtros: "Listos para Enviar", "Enviados", "Todos", "Problemáticos"
  - Contador de pedidos pendientes de envío
  - Tabla responsive con información clave de pedidos
- Implementar `frontend/src/components/admin/OrdersTable.vue`:
  - Tabla con sorting, filtering, pagination
  - Columns: Cliente, Pedido, Fecha, Estado, Tracking, Acciones
  - Bulk actions para múltiples pedidos
- Agregar a navegación admin existente con badge de contador

**Criterios de Aceptación**:
- ✅ Tabla maneja 1000+ pedidos sin performance issues
- ✅ Filtros permiten encontrar pedidos específicos rápidamente
- ✅ Bulk actions funcionan para hasta 50 pedidos simultáneamente
- ✅ Mobile responsive para acceso admin desde tablet
- ✅ Loading states durante operaciones que toman tiempo

**Dependencias**: Backend admin APIs funcionando (Sprint 1 Backend)  
**Entregables**: AdminShippingView, OrdersTable component, navegación admin

---

#### **T2.2: Componente de Gestión de Tracking** ⏱️ 24 horas
**Prioridad**: ALTA | **Complejidad**: Alta

**Descripción**: Interface para admins carguen tracking info y marquen pedidos como enviados.

**Subtareas**:
- Crear `frontend/src/components/admin/ShippingManager.vue`:
  - Selector de proveedor (Correo Argentino, OCA, Andreani)
  - Input validado para número de tracking con pattern validation
  - Botón "Marcar como Enviado" con confirmación
  - Preview de información que verá el cliente
- Implementar validación de tracking numbers por proveedor:
  - Correo Argentino: 13 dígitos, OCA: formato específico, etc.
- Modal de confirmación antes de marcar como enviado
- Success/error feedback con toasts informativas

**Criterios de Aceptación**:
- ✅ Validación previene tracking numbers inválidos por proveedor
- ✅ Preview muestra exactamente lo que verá el cliente
- ✅ Confirmación modal previene errores accidentales
- ✅ Feedback inmediato de éxito/error operaciones
- ✅ Form se resetea apropiadamente después de éxito

**Dependencias**: T2.1 (AdminShipping view) + Backend admin APIs  
**Entregables**: ShippingManager component, validadores de tracking

---

#### **T2.3: Simplificación de Checkout (Patrón Bohme)** ⏱️ 28 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Completar simplificación de checkout siguiendo patrón Bohme Clothes.

**Subtareas**:
- Finalizar pendientes en `frontend/src/views/checkout/CheckoutView.vue`:
  - Actualizar variables reactivas para nuevos campos de dirección
  - Corregir errores de TypeScript en props y emits
  - Simplificar flujo a 3 pasos: Carrito → Entrega → Pago
- Mejorar `frontend/src/components/checkout/AddressForm.vue`:
  - Campos separados: Calle, Número, Departamento, Barrio, Ciudad
  - Modal para editar código postal con autocompletado de ciudad
- Optimizar DeliveryProgress component existente para nuevo flujo
- Testing exhaustivo del nuevo flujo simplificado

**Criterios de Aceptación**:
- ✅ Flujo de 3 pasos es intuitivo y sin confusión
- ✅ Todas las variables reactivas funcionan correctamente
- ✅ TypeScript compila sin errores ni warnings
- ✅ Modal de código postal mejora UX significativamente
- ✅ Tests E2E del checkout completo pasan

**Dependencias**: Componentes existentes de checkout  
**Entregables**: CheckoutView simplificado, AddressForm mejorado

---

#### **T2.4: Optimización de OrdersView.vue** ⏱️ 18 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: Mejorar vista de historial de pedidos del usuario con tracking.

**Subtareas**:
- Rediseñar `frontend/src/views/orders/OrdersView.vue`:
  - Filtros por estado de envío (Todos, Pendientes, Enviados, Entregados)
  - Búsqueda por número de pedido
  - Preview de tracking number en lista de pedidos
  - Estado "Enviado" con ícono especial y fecha
- Implementar `frontend/src/components/orders/OrderCard.vue`:
  - Card design para cada pedido con información clave
  - Progress bar visual para estado de envío
  - Quick actions: Ver detalles, Copiar tracking
- Infinite scroll o pagination inteligente para usuarios con muchos pedidos

**Criterios de Aceptación**:
- ✅ Filtros permiten encontrar pedidos específicos rápidamente
- ✅ Búsqueda funciona por número de pedido y cliente
- ✅ Progress bars reflejan correctamente estado de envío
- ✅ Performance buena incluso con 100+ pedidos
- ✅ Mobile experience optimizada para touch

**Dependencias**: T1.3 (tracking integration)  
**Entregables**: OrdersView rediseñado, OrderCard component

---

#### **T2.5: Componentes de Soporte y Contacto** ⏱️ 12 horas
**Prioridad**: BAJA | **Complejidad**: Baja

**Descripción**: Componentes para mejorar experiencia de soporte al cliente.

**Subtareas**:
- Crear `frontend/src/components/support/ContactInfo.vue`:
  - Widget de información de contacto reutilizable
  - WhatsApp, email, horarios de atención
  - Enlaces que abren en app apropiada (WhatsApp, email client)
- Implementar `frontend/src/components/support/HelpCenter.vue`:
  - FAQ básico sobre envíos y tracking
  - Enlaces a políticas de envío y devoluciones
- Integrar componentes en OrderDetail y Dashboard
- Tracking de clicks en elementos de soporte (analytics opcional)

**Criterios de Aceptación**:
- ✅ Enlaces de contacto abren en apps apropiadas
- ✅ Información de contacto siempre visible donde es relevante
- ✅ FAQ responde preguntas comunes sobre envíos
- ✅ Design consistente con resto de la aplicación
- ✅ Mobile-optimized para touch interactions

**Dependencias**: Componentes de Sprint 1 completados  
**Entregables**: ContactInfo component, HelpCenter component

---

#### **T2.6: Testing e Integración Sprint 2** ⏱️ 26 horas
**Prioridad**: CRÍTICA | **Complejidad**: Media

**Descripción**: Testing exhaustivo de nuevas funcionalidades admin y user.

**Subtareas**:
- Unit tests para nuevos componentes:
  - AdminShippingView, ShippingManager, OrderCard
- Integration tests para flujos admin:
  - Login admin → ver pedidos → cargar tracking → marcar enviado
- E2E tests para checkout simplificado:
  - Agregar producto → checkout → pago → ver pedido
- Cross-browser testing en móvil y desktop
- Performance testing con grandes volúmenes de datos

**Criterios de Aceptación**:
- ✅ Coverage de tests >85% para componentes nuevos
- ✅ E2E tests cubren flujos críticos usuario y admin
- ✅ Performance tests validan responsiveness en móvil
- ✅ Cross-browser compatibility en Chrome, Firefox, Safari, Edge
- ✅ Accessibility testing pasa WCAG 2.1 AA básico

**Dependencias**: Todas las tareas T2.1-T2.5  
**Entregables**: Suite completa de tests, reporte de coverage

---

### **Definition of Done Sprint 2**
- [ ] Panel admin de envíos funcionando completamente
- [ ] Checkout simplificado a 3 pasos implementado
- [ ] OrdersView optimizado con filtros y búsqueda
- [ ] Componentes de soporte integrados donde corresponde
- [ ] Tests E2E pasan para flujos usuario y admin
- [ ] Performance en móvil validada y optimizada
- [ ] TypeScript sin errores en todo el codebase

---

## ⚡ SPRINT 3: Performance y Optimización Final (2 semanas - 80 horas)

### **Objetivo Sprint 3**
Optimizar performance, implementar Progressive Web App features y finalizar optimizaciones móvil.

### **Tareas Principales**

#### **T3.1: Optimización de Performance Frontend** ⏱️ 24 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Mejorar tiempos de carga y performance en runtime.

**Subtareas**:
- Code splitting estratégico para reducir bundle size:
  - Lazy loading de rutas admin y user dashboard
  - Dynamic imports para componentes pesados
- Optimización de imágenes:
  - WebP format con fallback, lazy loading mejorado
  - Placeholder blur-up technique para mejor UX
- Vue 3 performance optimizations:
  - `defineAsyncComponent` para componentes grandes
  - `v-memo` para listas que no cambian frecuentemente
- Bundle analysis y optimización de dependencias

**Criterios de Aceptación**:
- ✅ First Contentful Paint <1.5s en 3G slow
- ✅ Largest Contentful Paint <2.5s en 3G slow
- ✅ Bundle size reducido al menos 30%
- ✅ Core Web Vitals pasan en PageSpeed Insights
- ✅ Smooth 60fps scrolling en dispositivos mid-range

**Dependencias**: Componentes estables de sprints anteriores  
**Entregables**: Aplicación optimizada, métricas de performance mejoradas

---

#### **T3.2: Progressive Web App (PWA) Features** ⏱️ 18 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: Implementar funcionalidades PWA para experiencia mobile nativa.

**Subtareas**:
- Configurar Service Worker para caching estratégico:
  - Cache de assets estáticos (images, CSS, JS)
  - Network-first para API calls, cache-first para assets
- Implementar Web App Manifest:
  - Iconos para home screen, splash screen personalizada
  - Configuración para standalone mode
- Push notifications para updates de tracking (opcional):
  - Service worker para recibir notifications
  - User permission flow intuitivo
- Offline-first approach para funcionalidades básicas

**Criterios de Aceptación**:
- ✅ App instala correctamente en móvil como PWA
- ✅ Funciona offline para páginas previamente visitadas
- ✅ Push notifications llegan cuando tracking actualiza
- ✅ App startup time <1s después de instalación
- ✅ Native app-like experience en standalone mode

**Dependencias**: T3.1 (performance base optimizada)  
**Entregables**: PWA configurada, service worker, manifest

---

#### **T3.3: Mobile-First Optimización Completa** ⏱️ 16 horas
**Prioridad**: ALTA | **Complejidad**: Media

**Descripción**: Validar y optimizar experiencia mobile en todos los componentes.

**Subtareas**:
- Mobile UX audit de todos los flows críticos:
  - Login/register, browse products, checkout, view orders
- Touch target optimization (44px minimum)
- Gesture support donde sea apropiado:
  - Swipe en product galleries, pull-to-refresh en orders
- Keyboard handling para iOS/Android:
  - Proper input types, autocomplete attributes
- Performance en dispositivos low-end (Android <$200)

**Criterios de Aceptación**:
- ✅ Todos los touch targets cumplen 44px minimum
- ✅ Gestures funcionan intuitivamente sin conflicts
- ✅ Keyboard aparece con tipo correcto para cada input
- ✅ Performance aceptable en dispositivos low-end
- ✅ No horizontal scroll en ninguna pantalla mobile

**Dependencias**: Todos los componentes desarrollados  
**Entregables**: Mobile experience optimizada, gesture support

---

#### **T3.4: State Management y Data Flow Optimization** ⏱️ 14 horas
**Prioridad**: MEDIA | **Complejidad**: Media

**Descripción**: Optimizar stores Pinia y data flow para mejor performance.

**Subtareas**:
- Refactor Pinia stores para performance:
  - Memoization de getters costosos
  - Selective reactivity para objetos grandes
- Implement smart caching strategy:
  - Cache de user data, orders, product lists
  - TTL-based invalidation strategy
- Optimizar API calls:
  - Debouncing de search inputs
  - Request deduplication para calls simultáneas
- State persistence para mejor UX

**Criterios de Aceptación**:
- ✅ Stores no causan re-renders innecesarios
- ✅ API calls reducidas 50% con caching inteligente
- ✅ Search inputs no hammering backend
- ✅ State persiste apropiadamente entre sessions
- ✅ Memory usage optimizado para long sessions

**Dependencias**: Stores existentes estables  
**Entregables**: Stores optimizados, caching strategy implementada

---

#### **T3.5: Testing Final y Quality Assurance** ⏱️ 8 horas
**Prioridad**: CRÍTICA | **Complejidad**: Baja

**Descripción**: Testing exhaustivo y quality assurance pre-production.

**Subtareas**:
- Performance testing en diferentes dispositivos/browsers
- Accessibility testing completo con screen readers
- Security testing básico (XSS prevention, CSP headers)
- User acceptance testing con stakeholders
- Documentation de troubleshooting común

**Criterios de Aceptación**:
- ✅ Performance targets met en todos los dispositivos target
- ✅ Accessibility compliance WCAG 2.1 AA verificada
- ✅ Security testing no encuentra vulnerabilidades críticas
- ✅ UAT aprobado por stakeholders
- ✅ Troubleshooting guide documentada

**Dependencias**: Todas las implementaciones anteriores  
**Entregables**: Suite de testing completa, documentación QA

---

### **Definition of Done Sprint 3**
- [ ] Core Web Vitals pasan en todos los dispositivos target
- [ ] PWA instalable y funciona offline apropiadamente
- [ ] Mobile experience optimizada y touch-friendly
- [ ] State management optimizado sin performance issues
- [ ] Testing completo incluyendo accessibility y security
- [ ] Documentación de troubleshooting actualizada
- [ ] Ready for production deployment

---

## 📱 Especial Consideración: Dependencias con Backend

### **Dependencias Críticas**
- **Sprint 1**: Backend tracking APIs deben estar funcionando
- **Sprint 2**: Backend admin APIs completas y estables
- **Sprint 3**: Backend performance optimizado para loads altos

### **Comunicación con Backend Developer**
- Daily standups para sync en APIs
- Shared API documentation (Swagger) always updated
- Integration testing environments configured
- Error handling strategies aligned

---

## 📋 Resumen de Entregables por Sprint

### Sprint 1 (2 semanas)
- ✅ Navegación mejorada con "Mi Cuenta"
- ✅ Dashboard personal del usuario
- ✅ Integración completa tracking system
- ✅ OrderDetail con timeline visual
- ✅ Flujo post-compra optimizado
- **Total**: 80 horas

### Sprint 2 (3 semanas)
- ✅ Panel admin completo para envíos
- ✅ Checkout simplificado (3 pasos)
- ✅ OrdersView optimizado con filtros
- ✅ Componentes de soporte integrados
- ✅ Testing E2E comprehensivo
- **Total**: 120 horas

### Sprint 3 (2 semanas)
- ✅ Performance optimizado + PWA
- ✅ Mobile-first experience completa
- ✅ State management optimizado
- ✅ Quality assurance final
- **Total**: 80 horas

## 🎯 Métricas de Éxito Frontend

### Performance
- First Contentful Paint <1.5s
- Core Web Vitals passing en mobile
- Bundle size reducido 30%
- 60fps smooth scrolling

### User Experience
- Mobile conversion rate igual a desktop
- Support requests reducidos 60%
- User session duration aumentada 40%
- Mobile PWA adoption >20%

### Quality
- Test coverage >85% nuevos componentes
- Accessibility WCAG 2.1 AA compliant
- Cross-browser compatibility verified
- Zero TypeScript errors/warnings

---

**TOTAL ESTIMADO**: 280 horas (7 semanas) para Senior Frontend Developer

**Nota**: Este planning está sincronizado con backend planning. Coordinar sprints para máxima eficiencia del equipo.