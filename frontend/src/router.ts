import { nextTick } from 'vue'
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import HomeView from './views/shared/HomeView.vue'
import CollectionView from './views/products/CollectionView.vue'
import ProductDetailView from './views/products/ProductDetailView.vue'
import CheckoutView from './views/checkout/CheckoutView.vue'
import CartView from './views/cart/CartView.vue'
import AuthView from './views/auth/AuthView.vue'
import AdminUserManagementView from './views/admin/AdminUserManagementView.vue'
import AdminPaymentsView from './views/admin/AdminPaymentsView.vue'
import AdminOrdersView from './views/admin/AdminOrdersView.vue'
import PaymentSuccessView from './views/checkout/PaymentSuccessView.vue'
import PaymentFailureView from './views/checkout/PaymentFailureView.vue'
import PaymentPendingView from './views/checkout/PaymentPendingView.vue'
import PaymentReturnView from './views/checkout/PaymentReturnView.vue'
import TransferInstructionsView from './views/checkout/TransferInstructionsView.vue'
import CashConfirmationView from './views/checkout/CashConfirmationView.vue'
import { useAuthStore } from './store/auth';
import { COMPRAS_HABILITADAS } from './config/payments';
import { auth } from './config/index'; // Importar auth
import { globalProgressBar } from './composables/useProgressBar';
import ContactView from './views/shared/ContactView.vue';
import HowToShopView from './views/shared/HowToShopView.vue';
import ShippingView from './views/shared/ShippingView.vue';
import TermsView from './views/shared/TermsView.vue';
import PrivacyView from './views/shared/PrivacyView.vue';
import OrdersView from './views/orders/OrdersView.vue';
import OrderDetailView from './views/orders/OrderDetailView.vue';
import VerifyEmailView from './views/auth/VerifyEmailView.vue';
// @ts-ignore - Vue component import
import ProfileView from './views/profile/ProfileView.vue';
import AdminViewProduct from './views/admin/AdminViewProduct.vue';
import SizeGuideView from './views/shared/SizeGuideView.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', component: HomeView },
  { path: '/shop', component: CollectionView },
  { path: '/product/:id/:name?', component: ProductDetailView },
  { path: '/cart', component: CartView },
  { path: '/checkout', component: CheckoutView, meta: { requiresAuth: true } },
  { path: '/auth', component: AuthView },
  { path: '/verify-email', component: VerifyEmailView },
  { path: '/contact', component: ContactView },
  { path: '/how-to-shop', component: HowToShopView },
  { path: '/shipping', component: ShippingView, alias: '/retiro' },
  { path: '/terms', component: TermsView },
  { path: '/privacy', component: PrivacyView },
  { path: '/size-guide', component: SizeGuideView, alias: '/guia-de-talles' },
  // Orders routes
  { path: '/orders', component: OrdersView, meta: { requiresAuth: true } },
  { path: '/orders/:id', component: OrderDetailView, meta: { requiresAuth: true } },
  { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
  // Payment result routes
  { path: '/payment/return', component: PaymentReturnView },
  { path: '/payment/success', component: PaymentSuccessView },
  { path: '/payment/failure', component: PaymentFailureView },
  { path: '/payment/pending', component: PaymentPendingView },
  { path: '/payment/transfer-instructions', component: TransferInstructionsView },
  { path: '/payment/cash-confirmation', component: CashConfirmationView },
  {
    path: '/admin',
    redirect: '/admin/products'
  },
  {
    path: '/admin/products',
    component: AdminViewProduct,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    component: AdminUserManagementView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/payments',
    component: AdminPaymentsView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    component: AdminOrdersView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    // Si hay un hash (#section), ir a esa sección
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      };
    }
    // Por defecto, ir al top de la página
    return { top: 0 };
  }
});

// Guard para rutas protegidas
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  // Mostrar progress bar al cambiar de ruta
  if (to.path !== from.path) {
    globalProgressBar.start();
  }

  // Esperar a que se inicialice la autenticación si aún no se ha hecho
  if (authStore.loading) {
    // fetchUserRoles se ejecuta automáticamente después de fetchBackendUser en auth.ts:30
    // No necesitamos llamarlo aquí porque no hay token aún

    await new Promise(resolve => {
      const unsubscribe = auth.onAuthStateChanged((user: any) => {
        unsubscribe();
        resolve(user);
      });
    });
    await authStore.initAuth();
  }

  // Para rutas de admin, asegurar que los roles estén cargados
  if (to.meta.requiresAdmin && authStore.isAuthenticated) {
    // Early return si ya tiene acceso admin y roles cargados
    if (authStore.hasAdminAccess && authStore.userRoles.length > 0) {
      return next();
    }

    // Si no hay roles cargados, intentar cargarlos (con caché)
    if (authStore.userRoles.length === 0) {
      try {
        await authStore.fetchUserRoles(false); // false = usar caché si está disponible
      } catch (error) {
      }
    }

    // Verificación final sin logs innecesarios
    if (!authStore.hasAdminAccess) {
      next('/');
      return;
    }
  }

  // Si las compras online están deshabilitadas, redirigir /checkout al carrito
  if (!COMPRAS_HABILITADAS && to.path === '/checkout') {
    next('/cart');
    return;
  }

  // Verificar si la ruta requiere autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth');
  } else if (to.path === '/auth' && authStore.isAuthenticated) {
    // Si el usuario ya está autenticado, redirigir según sus roles
    if (authStore.hasAdminAccess) {
      next('/admin/products');
    } else {
      next('/');
    }
  } else {
    next();
  }
});

// Transición de ruta con View Transitions (sin soporte o con movimiento reducido: sin transición)
let terminarTransicion: (() => void) | null = null;

router.beforeResolve((to, from) => {
  if (
    !document.startViewTransition ||
    from.matched.length === 0 ||
    to.path === from.path ||
    matchMedia('(prefers-reduced-motion: reduce)').matches
  ) {
    return;
  }
  return new Promise<void>((resolve) => {
    document.startViewTransition(() => {
      resolve();
      return new Promise<void>((fin) => {
        terminarTransicion = fin;
        setTimeout(fin, 1000);
      });
    }).finished.catch(() => {});
  });
});

// Completar progress bar después de navegar
router.afterEach(() => {
  globalProgressBar.complete();
  if (terminarTransicion) {
    const fin = terminarTransicion;
    terminarTransicion = null;
    nextTick(fin);
  }
});

export default router;

