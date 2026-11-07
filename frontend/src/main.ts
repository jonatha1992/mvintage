import { createApp } from 'vue'
import { createPinia } from 'pinia'
import type { PluginOptions, POSITION } from 'vue-toastification'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import './style.css'
import './styles/admin-buttons.css'
import './styles/scroll-animations.css'
import App from './App.vue'
import router from './router'

// Type definitions for Vue plugins
declare module 'vue' {
  interface ComponentCustomProperties {
    $toast: typeof Toast
  }
}

const pinia = createPinia()
const app = createApp(App)

// Professional Toast configuration matching website branding
const toastOptions: PluginOptions = {
  position: 'top-right' as POSITION,
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
  transition: 'Vue-Toastification__fade',
  maxToasts: 2,
  newestOnTop: true,
  filterBeforeCreate: (toast, toasts) => {
    if (toasts.filter(t => t.type === toast.type).length !== 0) {
      // Prevent spam of same type
      return false;
    }
    return toast;
  }
}

// Initialize app with plugins
app.use(router)
app.use(pinia)
app.use(Toast, toastOptions)

// Initialize cart with session management before mounting the app
if (typeof window !== 'undefined') {
  // Import and initialize cart store before app mount
  import('./store/cart').then(({ useCartStore }) => {
    const cartStore = useCartStore()
    cartStore.initializeCart()
  }).catch(() => {})
}

// Mount app after cart initialization is started
app.mount('#app')
