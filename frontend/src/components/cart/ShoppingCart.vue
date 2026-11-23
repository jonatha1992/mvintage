<template>
  <div :class="isModal ? 'bg-white h-full' : 'bg-white min-h-screen'">
    <div :class="isModal ? 'px-4 py-6' : 'max-w-4xl mx-auto py-8 px-4 sm:py-12 sm:px-6 lg:px-8'">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-light tracking-tight text-gray-900 font-heading">Carrito de compras</h1>
        <p v-if="!cartStore.isEmpty" class="mt-2 text-sm font-body text-body-text">
          {{ cartStore.itemCount }} {{ cartStore.itemCount === 1 ? 'producto' : 'productos' }} en tu carrito
        </p>
      </div>

      <!-- Cart Items -->
      <div v-if="!cartStore.isEmpty" class="space-y-6">
        <!-- Items List -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
          <ul class="divide-y divide-gray-200">
            <li v-for="item in cartStore.items" :key="item.id" class="p-6">
              <div class="flex items-start space-x-4">
                <!-- Product Image -->
                <div class="flex-shrink-0">
                  <div class="w-20 h-20 overflow-hidden border border-gray-200 rounded-lg">
                    <img 
                      :src="item.product.images[0]?.image_url || '/placeholder-image.jpg'" 
                      :alt="item.product.name" 
                      class="object-cover object-center w-full h-full"
                    >
                  </div>
                </div>

                <!-- Product Details -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <h3 class="text-base font-medium text-gray-900 font-heading">
                        <router-link 
                          :to="`/product/${item.product.name}`" 
                          class="hover:text-gray-700 font-body"
                        >
                          {{ item.product.name }}
                        </router-link>
                      </h3>
                      
                      <!-- Variant Info -->
                      <div v-if="item.variant" class="mt-1 text-sm font-body text-body-text">
                        <span class="font-body">{{ item.variant.color.name }}</span>
                        <span class="mx-1 font-body">•</span>
                        <span class="font-body">Talle {{ item.variant.size.name }}</span>
                      </div>
                      
                      <!-- Unique Product Info -->
                      <div v-else-if="item.selectedColor || item.selectedSize" class="mt-1 text-sm font-body text-body-text">
                        <span v-if="item.selectedColor" class="font-body">{{ item.selectedColor.name }}</span>
                        <span v-if="item.selectedColor && item.selectedSize" class="mx-1 font-body">•</span>
                        <span v-if="item.selectedSize" class="font-body">Talle {{ item.selectedSize.name }}</span>
                      </div>
                    </div>

                    <!-- Item Total -->
                    <div class="ml-3 text-right shrink-0">
                      <p class="text-base font-semibold text-gray-900 font-body">
                        {{ formatPrice(cartStore.getItemTotal(item)) }}
                      </p>
                      <div v-if="item.product.has_discount" class="flex items-center justify-end space-x-1.5">
                        <span class="text-xs text-gray-400 line-through font-body">
                          {{ formatPrice(item.product.price * item.quantity) }}
                        </span>
                        <span class="text-xs font-medium text-red-600 font-body">
                          -{{ item.product.discount_percentage }}%
                        </span>
                      </div>
                      <p v-if="item.quantity > 1" class="text-xs text-gray-500 font-body">
                        {{ formatPrice(cartStore.getItemPrice(item)) }} c/u
                      </p>
                    </div>
                  </div>

                  <!-- Quantity Controls -->
                  <div class="flex items-center justify-between mt-3">
                    <div class="inline-flex items-center h-9 border border-gray-300 rounded-md">
                      <button
                        @click="updateQuantity(item, item.quantity - 1)"
                        :disabled="item.quantity <= 1"
                        class="w-9 h-full text-gray-700 hover:text-black disabled:text-gray-300 disabled:cursor-not-allowed"
                        aria-label="Restar uno"
                      >
                        −
                      </button>
                      <span class="w-8 text-sm text-center text-gray-900 tabular-nums" aria-live="polite">{{ item.quantity }}</span>
                      <button
                        @click="updateQuantity(item, item.quantity + 1)"
                        class="w-9 h-full text-gray-700 hover:text-black"
                        aria-label="Sumar uno"
                      >
                        +
                      </button>
                    </div>

                    <button
                      @click="cartStore.removeFromCart(item.id)"
                      class="text-xs text-gray-500 underline underline-offset-2 hover:text-gray-800"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Cart Summary -->
        <div class="p-6 border border-gray-200 rounded-lg bg-gray-50">
          <h3 class="mb-4 text-lg font-medium text-gray-900 font-heading">Resumen del pedido</h3>
          
          <div class="space-y-2">
            <!-- Subtotal -->
            <div class="flex justify-between text-sm">
              <span class="text-gray-600 font-body">Subtotal ({{ cartStore.itemCount }} {{ cartStore.itemCount === 1 ? 'producto' : 'productos' }})</span>
              <span class="text-gray-900 font-body">
                {{ formatPrice((cartStore.totalSavings > 0 ? cartStore.totalOriginalPrice : cartStore.totalPrice)) }}
              </span>
            </div>

            <!-- Discount -->
            <div v-if="cartStore.totalSavings > 0" class="flex justify-between text-sm">
              <span class="text-red-600 font-body">Descuentos</span>
              <span class="text-red-600 font-body">-{{ formatPrice(cartStore.totalSavings) }}</span>
            </div>

            <!-- Pickup -->
            <div class="flex justify-between text-sm">
              <span class="text-gray-600 font-body">Retiro en el local</span>
              <span class="text-gray-900 font-body">Gratis</span>
            </div>
            <p class="text-xs text-gray-500 font-body">
              <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline hover:text-gray-800">{{ STORE_PICKUP_ADDRESS }}</a> · {{ STORE_PICKUP_HOURS }}.
            </p>

            <!-- Total -->
            <div class="pt-2 border-t border-gray-200">
              <div class="flex justify-between">
                <span class="text-lg font-medium text-gray-900 font-body">Total</span>
                <span class="text-lg font-medium text-gray-900 font-body">
                  {{ formatPrice(cartStore.totalPrice) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Auth Notice -->
          <div v-if="COMPRAS_HABILITADAS && !authStore.isAuthenticated" class="p-3 mt-4 border border-blue-200 rounded-md bg-blue-50">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="w-5 h-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-blue-700 font-body">
                  Necesitás <strong>iniciar sesión</strong> para proceder con la compra.
                </p>
              </div>
            </div>
          </div>

          <!-- Online Purchases Disabled Notice -->
          <div v-if="!COMPRAS_HABILITADAS" class="p-3 mt-4 border border-amber-200 rounded-md bg-amber-50">
            <p class="text-sm text-amber-800 font-body">
              Las compras online estarán disponibles muy pronto.
            </p>
          </div>

          <!-- Checkout / WhatsApp Button -->
          <div class="mt-6">
            <button
              v-if="COMPRAS_HABILITADAS"
              @click="proceedToCheckout"
              class="w-full px-4 py-3 text-sm font-medium tracking-wide text-white uppercase whitespace-nowrap transition-colors bg-black rounded-md hover:bg-gray-800"
            >
              {{ authStore.isAuthenticated ? 'Finalizar compra' : 'Iniciar sesión para comprar' }}
            </button>
            <a
              v-else
              :href="whatsappCartUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="flex items-center justify-center w-full px-4 py-3 text-sm font-medium tracking-wide text-white uppercase whitespace-nowrap transition-colors bg-green-600 rounded-md hover:bg-green-700"
            >
              Consultar por WhatsApp
            </a>
          </div>

          <!-- Continue Shopping -->
          <div class="mt-4 text-center">
            <button
              @click="continueShopping"
              class="text-sm text-gray-600 cursor-pointer font-body hover:text-gray-800"
            >
              Continuar comprando
            </button>
          </div>
        </div>
      </div>

      <!-- Empty Cart -->
      <div v-else class="py-12 text-center">
        <div class="w-24 h-24 mx-auto mb-4 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-gray-900 font-heading">Tu carrito está vacío</h3>
        <p class="mb-6 text-gray-600 font-body">Agrega algunos productos para comenzar</p>
        <button
          @click="continueShopping"
          class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800"
        >
          Explorar productos
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatPrice } from '../../utils/price'
import { computed, onMounted, withDefaults } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore, type CartItem } from '../../store/cart';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { useCartModal } from '../../composables/useCartModal';
import { COMPRAS_HABILITADAS, WHATSAPP_NUMBER } from '../../config/payments';
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store';

// Props
interface Props {
  isModal?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  isModal: false
})

const cartStore = useCartStore();
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();
const { closeCartModal } = useCartModal();



onMounted(() => {
  // Cart is already initialized in main.ts, just validate stock if needed
  // Only validate stock when component mounts if cart has items
  if (!cartStore.isEmpty) {
    cartStore.validateStock();
  }
});

const updateQuantity = (item: CartItem, newQuantity: number) => {
  if (newQuantity < 1) return;
  
  // Check stock availability
  let maxStock = 0;
  if (item.product.is_unique) {
    maxStock = item.product.stock || 0;
  } else if (item.variant) {
    maxStock = item.variant.variant.stock;
  }
  
  if (newQuantity > maxStock) {
    toast.warning(`Solo hay ${maxStock} unidades disponibles`);
    return;
  }
  
  cartStore.updateQuantity(item.id, newQuantity);
};

const whatsappCartUrl = computed(() => {
  const lines = cartStore.items.map((item) => {
    const color = item.variant?.color?.name || item.selectedColor?.name;
    const size = item.variant?.size?.name || item.selectedSize?.name;
    const details = [color, size ? `Talle ${size}` : null].filter(Boolean).join(', ');
    const detailSuffix = details ? ` (${details})` : '';
    return `- ${item.product.name}${detailSuffix} x${item.quantity}: ${formatPrice(cartStore.getItemTotal(item))}`;
  });
  const nl = String.fromCharCode(10);
  const text = ['Hola! Quiero consultar por estos productos:', ...lines, `Total: ${formatPrice(cartStore.totalPrice)}`].join(nl);
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
});

const proceedToCheckout = () => {
  if (!COMPRAS_HABILITADAS) return;
  // Validate stock before proceeding
  cartStore.validateStock();
  
  if (cartStore.isEmpty) {
    toast.error('Tu carrito está vacío');
    return;
  }
  
  // Close modal if in modal mode
  if (props.isModal) {
    closeCartModal();
  }
  
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    toast.warning('Debes iniciar sesión para continuar con la compra');
    router.push('/auth');
    return;
  }
  
  // Navigate to checkout page
  router.push('/checkout');
};

const continueShopping = () => {
  // Close modal if in modal mode
  if (props.isModal) {
    closeCartModal();
  }
  
  // Navigate to shop
  router.push('/shop');
};
</script>

