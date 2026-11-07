<template>
  <div class="app-container" :class="{ 'app-loaded': appLoaded }">
    <Navbar />
    <router-view />
    <Footer v-if="shouldShowFooter && footerVisible" class="footer-delayed" />
    <!-- Progress Bar Global para navegación -->
    <ProgressBar
      :progress="progress"
      :is-visible="isVisible"
    />

    <!-- Loading Spinner para operaciones específicas solamente -->
    <LoadingSpinner
      :show="isLoading && !isVisible"
      :message="loadingMessage || 'Cargando...'"
      :submessage="loadingSubmessage"
    />
    <!-- Chatbot Component -->
    <Chatbot v-if="chatbotVisible" class="chatbot-delayed" />
    <!-- Cart Modal Component -->
    <CartModal />
    <!-- Cart Added Notification -->
    <CartAddedNotification />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './store/auth'
import { useProductsStore } from './store/products'
import { useLoading } from './composables/useLoading'
import { useScrollAnimation } from './composables/useScrollAnimation'
import Navbar from './components/layout/Navbar.vue'
import Footer from './components/layout/Footer.vue'
import LoadingSpinner from './components/ui/LoadingSpinner.vue'
import ProgressBar from './components/ui/ProgressBar.vue'
import Chatbot from './components/ui/Chatbot.vue'
import CartModal from './components/cart/CartModal.vue'
import CartAddedNotification from './components/cart/CartAddedNotification.vue'
import { globalProgressBar } from './composables/useProgressBar'

const route = useRoute()
const authStore = useAuthStore()
const productsStore = useProductsStore()
const { isLoading, loadingMessage, loadingSubmessage } = useLoading()
const { progress, isVisible } = globalProgressBar
const { addElements } = useScrollAnimation()

// Estado para controlar la animación de carga
const appLoaded = ref(false)
// Estado para controlar la visibilidad del footer con delay
const footerVisible = ref(false)
// Estado para controlar la visibilidad del chatbot con delay
const chatbotVisible = ref(false)

// Computed para determinar si el footer debe mostrarse
const shouldShowFooter = computed(() => {
  return !route.path.includes('/checkout')
})


// Función para inicializar animaciones de scroll
const initScrollAnimations = () => {
  // Add animations to common elements with stagger effect
  addElements('.product-card', { delay: 0, once: true })
  addElements('.hero-section h1, .hero-section h2', { delay: 200, once: true })
  addElements('.hero-section p', { delay: 400, once: true })
  addElements('.hero-section .btn', { delay: 600, once: true })
  addElements('.card', { delay: 0, once: true })
  addElements('.feature-item', { delay: 0, once: true })
  addElements('.testimonial', { delay: 0, once: true })
  addElements('footer > div > div', { delay: 0, once: true })
}

onMounted(async () => {
  // Inicialización con transición suave
  try {
    await authStore.initAuth()
    // Initialize products store globally
    console.log('🚀 App.vue - Initializing products store...')
    await productsStore.initialize()
    console.log('✅ App.vue - Products store initialized')
  } catch (error) {
    // La aplicación puede funcionar sin auth, no es crítico
    console.warn('Auth initialization failed:', error)
  } finally {
    // Pequeño delay para suavizar la transición
    setTimeout(() => {
      appLoaded.value = true
      // Inicializar animaciones después de que la app esté cargada
      initScrollAnimations()

      // Mostrar footer después de 2 segundos adicionales
      setTimeout(() => {
        footerVisible.value = true
      }, 2000)

      // Mostrar chatbot después de 3 segundos adicionales
      setTimeout(() => {
        chatbotVisible.value = true
      }, 3000)
    }, 100)
  }
})

onUnmounted(() => {
  // Cleanup handled by composables
})
</script>

<style scoped>
.app-container {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.4s ease-out, transform 0.4s ease-out;
}

.app-container.app-loaded {
  opacity: 1;
  transform: translateY(0);
}


/* Footer delayed entrance animation */
.footer-delayed {
  animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* Chatbot delayed entrance animation */
.chatbot-delayed {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* Ensure scroll animations work properly */
:deep(.scroll-animated) {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .app-container,
  .footer-delayed,
  .chatbot-delayed,
  :deep(.scroll-animated) {
    transition: none;
    animation: none;
  }

  .footer-delayed,
  .chatbot-delayed {
    opacity: 1;
    transform: none;
  }

  :deep(.animate-out),
  :deep(.animate-in) {
    opacity: 1;
    transform: none;
  }
}
</style>