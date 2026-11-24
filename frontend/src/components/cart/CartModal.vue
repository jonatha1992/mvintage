<template>
  <Teleport to="body">
    <!-- Modal Overlay -->
    <Transition name="panel">
      <div
        v-if="isCartModalOpen"
        class="fixed inset-0 z-50 overflow-hidden"
      >
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
          @click="closeCartModal"
        ></div>
        
        <!-- Modal Panel -->
        <div class="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl panel-slide">
          <!-- Close Button -->
          <button
            @click="closeCartModal"
                        aria-label="Cerrar carrito"
                        class="absolute top-2 right-2 z-10 flex items-center justify-center min-w-12 min-h-12 text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Cart Content -->
          <div class="h-full overflow-y-auto">
            <ShoppingCart :is-modal="true" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useCartModal } from '../../composables/useCartModal'
import ShoppingCart from './ShoppingCart.vue'

const { isCartModalOpen, closeCartModal } = useCartModal()
</script>
