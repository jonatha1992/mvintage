<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-3xl px-4 py-8 mx-auto sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8 text-center">
        <div class="w-16 h-16 mx-auto mb-4 text-green-600">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 class="text-3xl font-light text-gray-900">¡Pedido Confirmado!</h1>
        <p class="mt-2 text-lg text-gray-600">
          Orden #{{ orderData?.order_id || 'Cargando...' }}
        </p>
      </div>

      <div v-if="deliveryInfo" class="space-y-6">
        <!-- Información de Entrega -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-6 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Entrega a Domicilio
          </h2>
          
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Zona de Entrega</h3>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Zona:</span>
                    <span class="font-medium">{{ deliveryInfo.delivery_info.zone_name }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Tiempo estimado:</span>
                    <span class="font-medium">{{ deliveryInfo.estimated_delivery }}</span>
                  </div>
                  <p class="mt-2 text-xs text-gray-600">
                    {{ deliveryInfo.delivery_info.zone_description }}
                  </p>
                </div>
              </div>
              
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Dirección de Entrega</h3>
                <div class="text-sm">
                  <p class="font-medium">{{ deliveryInfo.customer_address }}</p>
                  <div v-if="customerInfo.address_reference || customerInfo.delivery_notes" class="mt-2 space-y-1">
                    <p v-if="customerInfo.address_reference" class="text-gray-600">
                      <span class="font-medium">Ref:</span> {{ customerInfo.address_reference }}
                    </p>
                    <p v-if="customerInfo.delivery_notes" class="text-gray-600">
                      <span class="font-medium">Notas:</span> {{ customerInfo.delivery_notes }}
                    </p>
                    <p v-if="customerInfo.preferred_delivery_time && customerInfo.preferred_delivery_time !== 'cualquiera'" class="text-gray-600">
                      <span class="font-medium">Horario preferido:</span> {{ formatDeliveryTime(customerInfo.preferred_delivery_time) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded">
                <h3 class="mb-3 font-medium text-gray-900">Resumen de Costos</h3>
                <div class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Subtotal productos:</span>
                    <span class="font-medium">${{ deliveryInfo.original_total.toLocaleString() }}</span>
                  </div>
                  
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Costo de envío:</span>
                    <span class="font-medium">
                      <span v-if="deliveryInfo.delivery_info.is_free" class="text-gray-400 line-through">
                        ${{ deliveryInfo.delivery_info.original_cost.toLocaleString() }}
                      </span>
                      <span :class="deliveryInfo.delivery_info.is_free ? 'text-green-600 ml-2' : ''">
                        {{ deliveryInfo.delivery_info.is_free ? 'GRATIS' : `$${deliveryInfo.delivery_cost.toLocaleString()}` }}
                      </span>
                    </span>
                  </div>
                  
                  <div v-if="deliveryInfo.delivery_info.is_free" class="flex justify-between text-sm text-green-600">
                    <span>Ahorro en envío:</span>
                    <span class="font-medium">${{ deliveryInfo.delivery_info.savings.toLocaleString() }}</span>
                  </div>
                  
                  <div class="pt-2 mt-3 border-t border-gray-200">
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-900">Total a pagar:</span>
                      <span class="text-xl font-bold text-green-600">
                        ${{ deliveryInfo.final_total.toLocaleString() }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="!deliveryInfo.delivery_info.is_free" class="p-4 border border-green-200 rounded bg-green-50">
                <h4 class="flex items-center mb-2 font-medium text-green-900">
                  <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  ¡Envio Gratis!
                </h4>
                <p class="text-sm text-green-800">
                  El envío es gratuito para compras superiores a
                  <span class="font-medium">${{ deliveryInfo.delivery_info.free_threshold.toLocaleString() }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Instrucciones -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="flex items-center mb-4 text-xl font-medium text-gray-900">
            <svg class="w-6 h-6 mr-2 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Instrucciones para la Entrega
          </h2>
          
          <div class="space-y-3">
            <div v-for="(instruction, index) in deliveryInfo.instructions" :key="index" class="flex items-start">
              <div class="flex-shrink-0 h-6 w-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                {{ index + 1 }}
              </div>
              <p class="text-gray-700">{{ instruction }}</p>
            </div>
          </div>
        </div>

        <!-- Información del Cliente -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-xl font-medium text-gray-900">Información de Contacto</h2>
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div>
              <h3 class="mb-2 font-medium text-gray-900">Datos del Comprador</h3>
              <div class="space-y-1 text-sm">
                <p><span class="text-gray-600">Nombre:</span> {{ customerInfo.name }}</p>
                <p><span class="text-gray-600">Email:</span> {{ customerInfo.email }}</p>
                <p><span class="text-gray-600">Teléfono:</span> {{ customerInfo.phone }}</p>
              </div>
            </div>
            <div>
              <h3 class="mb-2 font-medium text-gray-900">Método de Pago</h3>
              <div class="flex items-center text-sm">
                <svg class="w-5 h-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span class="font-medium">Efectivo contra entrega</span>
              </div>
              <p class="mt-1 text-xs text-gray-600">
                Paga cuando recibas tu pedido
              </p>
            </div>
          </div>
        </div>

        <!-- Estado del Pedido -->
        <div class="p-6 bg-white rounded-lg shadow">
          <h2 class="mb-4 text-xl font-medium text-gray-900">¿Qué sigue?</h2>
          
          <div class="space-y-4">
            <div class="flex items-start">
              <div class="flex items-center justify-center flex-shrink-0 w-8 h-8 mr-4 text-sm font-medium text-green-600 bg-green-100 rounded-full">
              </div>
              <div>
                <h3 class="font-medium text-gray-900">Pedido Confirmado</h3>
                <p class="text-sm text-gray-600">Tu pedido ha sido registrado exitosamente</p>
              </div>
            </div>
            
            <div class="flex items-start">
              <div class="flex items-center justify-center flex-shrink-0 w-8 h-8 mr-4 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
                2
              </div>
              <div>
                <h3 class="font-medium text-gray-900">Coordinación de Entrega</h3>
                <p class="text-sm text-gray-600">Te contactaremos en las próximas 24 horas para coordinar la entrega</p>
              </div>
            </div>
            
            <div class="flex items-start">
              <div class="flex items-center justify-center flex-shrink-0 w-8 h-8 mr-4 text-sm font-medium text-gray-600 bg-gray-100 rounded-full">
                3
              </div>
              <div>
                <h3 class="font-medium text-gray-900">Entrega y Pago</h3>
                <p class="text-sm text-gray-600">Recibes tu pedido y pagas en efectivo</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones -->
        <div class="p-6 bg-white rounded-lg shadow">
          <div class="flex flex-col gap-4 sm:flex-row">
            <button
              @click="goHome"
              class="flex-1 px-4 py-3 font-medium text-white transition-colors bg-gray-900 rounded-md hover:bg-gray-800"
            >
              Volver al Inicio
            </button>
            
            <button
              @click="goToShop"
              class="flex-1 px-4 py-3 font-medium text-gray-700 transition-colors border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Seguir Comprando
            </button>
          </div>
          
          <p class="mt-4 text-xs text-center text-gray-500">
            Recibirás un email de confirmación con estos datos. Te contactaremos pronto para coordinar la entrega.
          </p>
        </div>
      </div>

      <!-- Loading state -->
      <div v-else class="py-12 text-center">
        <div class="w-12 h-12 mx-auto mb-4 border-b-2 border-green-600 rounded-full animate-spin"></div>
        <p class="text-gray-600">Cargando información de entrega...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useProducts } from '../../store/products';
import type { DeliveryInfo, Customer } from '../../types';

const router = useRouter();
const toast = useToast();
const { invalidateCache } = useProducts();

const orderData = ref<any>(null);
const deliveryInfo = ref<DeliveryInfo | null>(null);
const customerInfo = ref<Customer | any>({});

onMounted(() => {
  // Clear products cache on cash purchase confirmation
  // This ensures fresh stock data is fetched next time
  invalidateCache();

  const storedData = localStorage.getItem('cash_order');
  if (storedData) {
    try {
      const data = JSON.parse(storedData);
      orderData.value = data;
      deliveryInfo.value = data.delivery_info;
      customerInfo.value = data.customer;

      // Clear stored data to prevent reuse
      localStorage.removeItem('cash_order');
    } catch (error) {
      toast.error('Error cargando datos de entrega');
      router.push('/');
    }
  } else {
    toast.warning('No se encontraron datos de entrega');
    router.push('/');
  }
});

const formatDeliveryTime = (time: string) => {
  const timeMap: Record<string, string> = {
    'mañana': 'Mañana (9:00 - 13:00)',
    'tarde': 'Tarde (14:00 - 18:00)', 
    'noche': 'Noche (18:00 - 21:00)',
    'cualquiera': 'Cualquier horario'
  };
  return timeMap[time] || time;
};

const goHome = () => {
  router.push('/');
};

const goToShop = () => {
  router.push('/shop');
};
</script>
