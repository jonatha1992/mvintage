<template>
  <div class="min-h-screen bg-gray-50 lg:h-screen lg:overflow-hidden">
    <div class="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8 lg:h-full lg:flex lg:flex-col">
      <!-- Header -->
      <div class="mb-6">
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2">
            <li>
              <router-link to="/cart" class="text-gray-400 hover:text-gray-500 flex items-center">
                <svg class="flex-shrink-0 w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="ml-1 text-sm font-body">Carrito</span>
              </router-link>
            </li>
            <li>
              <div class="flex items-center">
                <svg class="flex-shrink-0 w-4 h-4 text-gray-300" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="ml-2 text-sm font-medium font-body text-body-text">Checkout</span>
              </div>
            </li>
          </ol>
        </nav>
        <h1 class="mt-3 text-2xl font-light text-gray-900 font-heading">Finalizar compra</h1>
        
        <!-- Delivery Progress -->
        <div class="mt-4">
          <DeliveryProgress 
            :current-step="currentStep" 
            @go-to-step="handleGoToStep"
          />
        </div>
      </div>

      <!-- Content -->
      <div v-if="!cartStore.isEmpty" class="lg:grid lg:grid-cols-2 lg:gap-x-12 lg:items-start lg:flex-1 lg:overflow-hidden">
        <!-- Order Summary -->
        <div class="order-2 lg:order-1 lg:h-full lg:flex lg:flex-col">
          <div class="p-6 bg-white rounded-lg shadow">
            <h2 class="mb-4 text-lg font-medium text-gray-900 font-heading">Resumen del pedido</h2>
            
            <!-- Items -->
            <ul class="mb-6 divide-y divide-gray-200">
              <li v-for="item in cartStore.items" :key="item.id" class="flex py-4">
                <!-- Image -->
                <div class="flex-shrink-0">
                  <img 
                    :src="item.product.images[0]?.image_url || '/placeholder-image.jpg'"
                    :alt="item.product.name"
                    class="object-cover object-center w-16 h-16 rounded-md"
                  >
                </div>
                
                <!-- Details -->
                <div class="flex-1 ml-4">
                  <div class="flex justify-between">
                    <div>
                      <h3 class="text-sm font-medium text-gray-900 font-heading">{{ item.product.name }}</h3>
                      
                      <!-- Variant Info -->
                      <div v-if="item.variant" class="mt-1 text-sm font-body text-body-text">
                        {{ item.variant.color.name }} • Talle {{ item.variant.size.name }}
                      </div>
                      
                      <!-- Unique Product Info -->
                        <div v-else-if="item.selectedColor || item.selectedSize" class="mt-1 text-sm font-body text-body-text">
                          <span v-if="item.selectedColor" class="font-body">{{ item.selectedColor.name }}</span>
                        <span v-if="item.selectedColor && item.selectedSize" class="font-body"></span>
                        <span v-if="item.selectedSize" class="font-body">Talle {{ item.selectedSize.name }}</span>
                      </div>
                      
                      <p class="mt-1 text-sm font-body text-body-text">Cantidad: {{ item.quantity }}</p>
                    </div>
                    
                    <div class="text-right">
                      <p class="text-sm font-medium font-body text-body-text">
                        {{ formatPrice(cartStore.getItemTotal(item)) }}
                      </p>
                      <p v-if="isProductDiscountActive(item.product)" class="text-xs line-through font-body text-body-text">
                        {{ formatPrice((item.product.price * item.quantity)) }}
                      </p>
                      <p v-if="item.quantity > 1" class="text-xs text-gray-500 font-body">
                        {{ formatPrice(cartStore.getItemPrice(item)) }} c/u
                      </p>
                    </div>
                  </div>
                </div>
              </li>
            </ul>

            <!-- Totals -->
            <div class="pt-4 space-y-2 border-t border-gray-200">
              <div class="flex justify-between text-sm">
                <span class="font-body text-body-text">Subtotal</span>
                <span class="font-body text-body-text">
                  {{ formatPrice((cartStore.totalSavings > 0 ? cartStore.totalOriginalPrice : cartStore.totalPrice)) }}
                </span>
              </div>
              
              <div v-if="cartStore.totalSavings > 0" class="flex justify-between text-sm">
                <span class="text-red-600 font-body">Descuentos</span>
                <span class="text-red-600 font-body">-{{ formatPrice(cartStore.totalSavings) }}</span>
              </div>

              <div class="flex justify-between text-sm">
                <span class="font-body text-body-text">Retiro en el local</span>
                <span class="font-body text-body-text">Gratis</span>
              </div>
              
              <div class="pt-2 border-t border-gray-200">
                <div class="flex justify-between">
                  <span class="text-base font-medium font-body text-body-text">Total</span>
                  <span class="text-base font-medium font-body text-body-text">
                    {{ formatPrice(cartStore.totalPrice) }}
                  </span>
                </div>
              </div>
            </div>
          </div>


        </div>

        <!-- Checkout Form -->
        <div class="order-1 lg:order-2 lg:h-full lg:overflow-y-auto lg:pr-4">
          <form ref="checkoutFormElement" @submit.prevent="processOrder" class="space-y-6">
            <!-- Step 2: Delivery Info (incluye datos de contacto) -->
            <div v-if="currentStep === 2">
              <button type="button" class="min-h-11 px-3 mb-3 underline" @click="handleGoToStep(1)">Volver al carrito</button>
              <ContactInfoStep
                :first-name="checkoutForm.firstName"
                :last-name="checkoutForm.lastName"
                :email="checkoutForm.email"
                :phone="checkoutForm.phone"
                :phone-country-code="checkoutForm.phoneCountryCode"
                :loading-user-data="loadingUserData"
                :using-previous-data="usingPreviousData"
                @update:firstName="checkoutForm.firstName = $event"
                @update:lastName="checkoutForm.lastName = $event"
                @update:email="checkoutForm.email = $event"
                @update:phone="checkoutForm.phone = $event"
                @update:phoneCountryCode="checkoutForm.phoneCountryCode = $event"
              />
              <DeliveryStep
                class="mt-6"
                :contact-complete="Boolean(isContactInfoComplete)"
                @delivery-method-changed="handleDeliveryMethodChange"
                @continue="handleContinueToPayment"
              />
            </div>

            <!-- Step 3: Payment Method -->
            <div v-if="currentStep === 3" class="p-6 bg-white rounded-lg shadow" data-payment-section>
              <h2 id="payment-heading" tabindex="-1" class="mb-4 text-lg font-medium text-gray-900 font-heading">Método de pago</h2>
              <p class="mb-4 text-sm text-gray-700">Retiro en el local · {{ STORE_PICKUP_ADDRESS }}. {{ STORE_PICKUP_HOURS }}.</p>
              <button type="button" class="min-h-11 px-3 mb-4 underline" @click="handleGoToStep(2)">Volver al contacto</button>
              
              <div class="space-y-3">
                <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    v-model="checkoutForm.paymentMethod"
                    type="radio"
                    value="transfer"
                    class="w-4 h-4 text-black border-gray-300 focus:ring-black"
                  >
                  <BanknotesIcon class="w-5 h-5 ml-3 text-blue-600" />
                  <span class="ml-2 text-sm font-body">Transferencia bancaria</span>
                </label>
                
                <label
                  class="flex items-start p-3 border border-gray-200 rounded-lg"
                  :class="MERCADOPAGO_HABILITADO ? 'cursor-pointer hover:bg-gray-50' : 'cursor-not-allowed opacity-60 bg-gray-50'"
                >
                  <input
                    v-model="checkoutForm.paymentMethod"
                    type="radio"
                    value="mercadopago"
                    :disabled="!MERCADOPAGO_HABILITADO"
                    class="w-4 h-4 mt-0.5 text-black border-gray-300 focus:ring-black disabled:cursor-not-allowed"
                  >
                  <CreditCardIcon class="w-5 h-5 ml-3 text-purple-600 shrink-0" />
                  <div class="ml-2">
                    <span class="block text-sm font-body">Mercado Pago</span>
                    <span v-if="!MERCADOPAGO_HABILITADO" class="block mt-1 text-xs text-gray-500 font-body">
                      Por el momento no se encuentra habilitado el pago con Mercado Pago.
                    </span>
                  </div>
                </label>
              </div>
              
              <!-- Botón Finalizar Compra -->
              <div v-if="checkoutForm.paymentMethod" class="mt-6">
                <button
                  type="submit"
                  :disabled="processing"
                  class="w-full px-6 py-3 font-medium text-white transition-all duration-200 bg-black rounded-md hover:bg-gray-800 motion-safe:active:scale-[0.98] disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  <span v-if="processing" class="text-white">Procesando...</span>
                  <span v-else class="text-white">Finalizar compra</span>
                </button>
                
                <p class="mt-3 text-xs text-center font-body text-body-text">
                  Al finalizar tu compra, aceptas nuestros términos y condiciones
                </p>
              </div>
            </div>


          </form>
        </div>
      </div>

      <!-- Empty Cart Message -->
      <div v-else class="py-12 text-center">
        <div class="w-24 h-24 mx-auto mb-4 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <h3 class="mb-2 text-lg font-medium text-gray-900 font-heading">Tu carrito está vacío</h3>
        <p class="mb-6 font-body text-body-text">Agrega algunos productos antes de finalizar tu compra</p>
        <router-link
          to="/shop"
          class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-black border border-transparent rounded-md hover:bg-gray-800"
        >
          <span>Continuar comprando</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { orderAccessToken } from '../../utils/orderAccess';
import { formatPrice, getEffectivePrice, isProductDiscountActive } from '../../utils/price'
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '../../store/cart';
import { useAuthStore } from '../../store/auth';
import { useToast } from 'vue-toastification';
import { ordersApi, customersApi, orderItemsApi, paymentsApi } from '../../config/api';
import { COMPRAS_HABILITADAS, MERCADOPAGO_HABILITADO } from '../../config/payments'
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store'
import { stockService } from '../../services/stockService';
import { isValidPhone, formatE164, splitStoredPhone, validationMessages } from '../../composables/useValidators';
import { useUserData } from '../../composables/useUserData';
import type { PaymentMethod, Order, CustomerCreate, OrderItemCreate } from '../../types';
import DeliveryProgress from '../../components/ui/DeliveryProgress.vue';
import ContactInfoStep from '../../components/checkout/ContactInfoStep.vue';
import DeliveryStep from '../../components/checkout/DeliveryStep.vue';
import { BanknotesIcon, CreditCardIcon } from '@heroicons/vue/24/outline';

const cartStore = useCartStore();
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();
const { loadCustomerData, getCheckoutFormData } = useUserData();

// Ref para la sección de método de pago
const checkoutFormElement = ref<HTMLFormElement | null>(null);

const processing = ref(false);
const loadingUserData = ref(false);
const usingPreviousData = ref(false);

const checkoutForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  phoneCountryCode: 'AR',
  address: '',
  streetNumber: '',
  fullAddress: '',
  city: '',
  postalCode: '',
  province: '',
  country: 'AR',
  addressReference: '',
  deliveryNotes: '',
  preferredDeliveryTime: 'cualquiera',
  paymentMethod: 'transfer',
  deliveryMethod: ''
});

// Delivery method and cost
const deliveryMethod = ref('retiro_local');

// New 3-step flow state management
const currentStep = ref(2); // Start at step 2 (Delivery Info)

// Check if each step is complete
const isContactInfoComplete = computed(() => {
  return checkoutForm.value.firstName.trim() && 
         checkoutForm.value.lastName.trim() && 
         checkoutForm.value.email.trim() && 
         isValidPhone(checkoutForm.value.phone, checkoutForm.value.phoneCountryCode);
});

const isDeliveryInfoComplete = computed(() => {
  return deliveryMethod.value === 'retiro_local' && Boolean(isContactInfoComplete.value);
});

const focusStep = async (step: 2 | 3) => {
  currentStep.value = step;
  await nextTick();
  const heading = document.getElementById(step === 2 ? 'contact-heading' : 'payment-heading');
  heading?.focus({ preventScroll: true });
  heading?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
};

const goToPaymentStep = () => {
  if (checkoutFormElement.value?.reportValidity() && isDeliveryInfoComplete.value) {
    void focusStep(3);
  }
};


// Function to handle step navigation
const handleGoToStep = (step: number) => {
  if (step === 1) {
    // Navigate back to cart
    router.push('/cart');
  } else if (step === 2) {
    void focusStep(2);
  } else if (step === 3 && isDeliveryInfoComplete.value) {
    goToPaymentStep();
  }
};

// Métodos para manejar eventos del DeliveryStep
const handleDeliveryMethodChange = (data: { method: string; cost: number }) => {
  deliveryMethod.value = data.method;
};

const handleContinueToPayment = () => {
  goToPaymentStep();
};

onMounted(async () => {
  if (!COMPRAS_HABILITADAS) {
    router.replace('/cart');
    return;
  }

  // Check authentication first
  if (!authStore.isAuthenticated) {
    toast.warning('Debes iniciar sesión para finalizar tu compra');
    router.push('/auth');
    return;
  }
  
  // Load cart from localStorage
  cartStore.loadFromStorage();
  
  // Redirect if cart is empty
  if (cartStore.isEmpty) {
    toast.warning('Tu carrito está vacío');
    router.push('/cart');
    return;
  }
  
  // Load customer data automatically if user is authenticated
  loadingUserData.value = true;
  try {
    const customerData = await loadCustomerData();
    
    if (customerData) {
      // User has previous purchase data - auto-populate form
      const formData = getCheckoutFormData();
      Object.assign(checkoutForm.value, formData);
      const storedPhone = splitStoredPhone(checkoutForm.value.phone, checkoutForm.value.phoneCountryCode || 'AR');
      checkoutForm.value.phone = storedPhone.national;
      checkoutForm.value.phoneCountryCode = storedPhone.country;
      
      usingPreviousData.value = true;
      
      toast.success('Datos cargados desde compra anterior', { timeout: 2000 });
    } else {
      // First-time buyer - only pre-fill basic info from auth
      if (authStore.backendUser) {
        checkoutForm.value.email = authStore.backendUser.email;
        if (authStore.backendUser.name) {
          const nameParts = authStore.backendUser.name.split(' ');
          checkoutForm.value.firstName = nameParts[0] || '';
          checkoutForm.value.lastName = nameParts.slice(1).join(' ') || '';
          
        }
      }
    }
  } catch (error) {
    // Fallback to basic auth info
    if (authStore.backendUser) {
      checkoutForm.value.email = authStore.backendUser.email;
      if (authStore.backendUser.name) {
        const nameParts = authStore.backendUser.name.split(' ');
        checkoutForm.value.firstName = nameParts[0] || '';
        checkoutForm.value.lastName = nameParts.slice(1).join(' ') || '';
        
      }
    }
  } finally {
    loadingUserData.value = false;
  }
  
  // Validate stock
  cartStore.validateStock();
});


const processOrder = async () => {
  if (!COMPRAS_HABILITADAS) {
    router.replace('/cart');
    return;
  }

  // Ensure we're on the payment step
  if (currentStep.value !== 3) {
    toast.error('Debes completar todos los pasos antes de confirmar el pedido');
    return;
  }

  // Double-check authentication
  if (!authStore.isAuthenticated) {
    toast.error('Debes iniciar sesión para completar la compra');
    router.push('/auth');
    return;
  }
  
  if (cartStore.isEmpty) {
    toast.error('Tu carrito está vacío');
    return;
  }
  
  try {
    // Validate stock with backend using the new stock service
    processing.value = true;
    
    // Prepare items for stock check
    const stockCheckItems = cartStore.items.map(item => ({
      product_id: item.product.id,
      variant_id: item.variant?.variant.id,
      quantity: item.quantity
    }));

    // Check stock with backend
    const stockResponse = await cartStore.validateStock();
    
    if (stockResponse.hasStockIssues) {
      // The cart store already handles showing notifications and updating quantities
      // Just redirect to cart to show the changes
      router.push('/cart');
      return;
    }
    
    if (cartStore.isEmpty) {
      toast.error('Algunos productos ya no están disponibles');
      router.push('/cart');
      return;
    }
    
    // Retiro local solo requiere datos de contacto válidos.
    const validateForm = () => {
      if (!isValidPhone(checkoutForm.value.phone, checkoutForm.value.phoneCountryCode)) {
        toast.error(validationMessages.phone);
        return false;
      }
      if (!checkoutForm.value.firstName.trim() || !checkoutForm.value.lastName.trim() || !checkoutForm.value.email.trim()) {
        toast.error('Completá nombre, apellido y email.');
        return false;
      }
      return true;
    };

    if (!validateForm()) {
      processing.value = false;
      return;
    }

    if (checkoutForm.value.paymentMethod === 'mercadopago' && !MERCADOPAGO_HABILITADO) {
      toast.error('Por el momento no se encuentra habilitado el pago con Mercado Pago.');
      checkoutForm.value.paymentMethod = 'transfer';
      processing.value = false;
      return;
    }

    // Step 1: Create customer
    const normalizedPhone = formatE164(checkoutForm.value.phone, checkoutForm.value.phoneCountryCode);
    const customerData: CustomerCreate = {
      name: `${checkoutForm.value.firstName} ${checkoutForm.value.lastName}`,
      first_name: checkoutForm.value.firstName,
      last_name: checkoutForm.value.lastName,
      email: checkoutForm.value.email,
      phone: normalizedPhone,
      address: checkoutForm.value.address || 'Retiro en el local',
      city: checkoutForm.value.city,
      postal_code: checkoutForm.value.postalCode,
      province: checkoutForm.value.province,
      country: checkoutForm.value.country,
      address_reference: checkoutForm.value.addressReference,
      delivery_notes: checkoutForm.value.deliveryNotes,
      preferred_delivery_time: checkoutForm.value.preferredDeliveryTime
    };
    
    const customer = await customersApi.createCustomer(customerData);
    
    // Step 2: Create order with real customer_id
    const orderData: Partial<Order> = {
      customer_id: customer.id,
      total: cartStore.totalPrice,
      payment_method: checkoutForm.value.paymentMethod === 'transfer' ? 'bank_transfer' : 'mercadopago',
      delivery_method: deliveryMethod.value,
    };
    
    const response = await ordersApi.createOrder(orderData);
    orderAccessToken(response.order.id, response.access_token);
    
    // Step 3: Create order items
    for (const item of cartStore.items) {
      // FINAL stock check right before creating order item
      try {
        // Use the stock service for final verification
        const finalStockCheck = await stockService.checkStock([{
          product_id: item.product.id,
          variant_id: item.variant?.variant.id,
          quantity: item.quantity
        }]);

        const itemResult = finalStockCheck.items[0];
        
        if (!itemResult.has_enough_stock) {
          throw new Error(`Stock insuficiente para "${item.product.name}". Stock disponible: ${itemResult.available_stock}, solicitado: ${item.quantity}`);
        }
        
        // Update local stock information
        if (item.product.is_unique) {
          item.product.stock = itemResult.available_stock;
        } else if (item.variant) {
          item.variant.variant.stock = itemResult.available_stock;
        }
        
      } catch (error: any) {
        if (error.message?.includes('Stock insuficiente')) {
          throw error;
        }
        // If it's an API error, continue with order item creation
      }
      
      const itemPrice = getEffectivePrice(item.product);
      
      // Crear order item data simplificado que coincide exactamente con el backend
      const orderItemData: OrderItemCreate = {
        order_id: response.order.id,
        product_id: item.product.id,
        variant_id: item.variant?.variant.id,
        quantity: item.quantity,
        price: itemPrice
      };
      
      try {
        await orderItemsApi.createOrderItem(orderItemData);
      } catch (error: any) {
        throw error; // Re-throw to be caught by outer try-catch
      }
    }

    try {
      await ordersApi.notifyOrderCreated(response.order.id);
    } catch (notifyError) {
      console.warn('No se pudo enviar la notificación del pedido:', notifyError);
    }
    
    // Step 4: Handle different payment methods
    if (checkoutForm.value.paymentMethod === 'mercadopago') {
      try {
        const preference = await paymentsApi.createPreference(response.order.id);
        const checkoutUrl = preference?.checkoutUrl || preference?.checkout_url || preference?.init_point;
        if (!checkoutUrl) {
          toast.error('No se pudo obtener el enlace de pago de Mercado Pago. Tu carrito sigue guardado.');
          return;
        }
        localStorage.setItem('pending_order', JSON.stringify({
          order_id: response.order.id,
          customer: customer,
          total: cartStore.totalPrice,
          items: cartStore.items
        }));
        window.location.href = checkoutUrl;
      } catch (mpError: any) {
        const detail = mpError?.response?.data?.detail;
        toast.error(detail || 'El pago con Mercado Pago no está disponible en este momento. Tu carrito sigue guardado.');
        return;
      }
    } else if (checkoutForm.value.paymentMethod === 'transfer') {
      // Clear cart and redirect to transfer instructions
      cartStore.clearCart();
      
      // Store transfer info for instruction page
      localStorage.setItem('transfer_order', JSON.stringify({
        order_id: response.order.id,
        customer: customer,
        transfer_info: response.transfer_info
      }));
      
      toast.success('¡Pedido confirmado! Te mostraremos los datos de transferencia.');
      router.push('/payment/transfer-instructions');
    } else {
      toast.error('Método de pago no disponible. Seleccioná transferencia bancaria.');
    }
    
  } catch (error: any) {
    
    // Handle specific stock error
    if (error.response?.data?.detail?.includes('Stock insuficiente')) {
      toast.error('No hay suficiente stock para algunos productos. Revisa tu carrito.');
      // Refresh cart to update stock
      cartStore.validateStock();
      if (!cartStore.isEmpty) {
        router.push('/cart');
      }
    } else {
      toast.error('Error al procesar el pedido. Por favor intenta nuevamente.');
    }
  } finally {
    processing.value = false;
  }
};
</script>
