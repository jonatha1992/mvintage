<template>
  <div class="space-y-6">
    
    <!-- Loading State Global -->
    <div v-if="isLoadingQuotes" class="bg-white shadow rounded-lg p-6">
      <div class="py-4 text-center">
        <div class="inline-flex items-center">
          <svg class="w-5 h-5 mr-3 -ml-1 text-gray-500 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-sm text-gray-600">Cotizando envíos...</span>
        </div>
      </div>
    </div>

    <!-- Error/Warning Message Global -->
    <div v-if="quotesError && !isLoadingQuotes" class="bg-white shadow rounded-lg p-6">
      <div class="p-3 border border-yellow-200 rounded-lg bg-yellow-50">
        <div class="flex">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p class="ml-2 text-sm text-yellow-800">{{ quotesError }}</p>
        </div>
      </div>
    </div>
      
      <!-- PASO 1: SELECCIÓN DE TIPO DE ENTREGA -->
      <div v-if="showDeliveryTypeSelection" class="bg-white shadow rounded-lg p-6">
        <h3 class="font-heading text-lg font-medium text-gray-900 mb-4">¿Cómo querés recibir tu pedido?</h3>
        
        <!-- Retiro en local -->
        <div class="provider-option mb-4 p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             :class="deliveryType === 'retiro_local' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
             @click="selectDeliveryType('retiro_local')">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <span class="text-2xl mr-3">🏠</span>
              <div>
                <h4 class="font-medium text-gray-900">Retiro en local</h4>
                <p class="text-sm text-gray-500">Coordinar retiro en nuestro local</p>
              </div>
            </div>
            <span class="text-lg font-medium text-green-600">Gratis</span>
          </div>
        </div>
        
        <!-- Envío a domicilio -->
        <div class="provider-option mb-4 p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
             :class="deliveryType === 'envio_domicilio' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
             @click="selectDeliveryType('envio_domicilio')">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <span class="text-2xl mr-3">🚚</span>
              <div>
                <h4 class="font-medium text-gray-900">Envío a domicilio</h4>
                <p class="text-sm text-gray-500">Recibí tu pedido en tu casa</p>
              </div>
            </div>
            <span class="text-lg font-medium text-gray-900">Ver opciones</span>
          </div>
        </div>
        
        <!-- Botón continuar -->
        <div v-if="deliveryType" class="text-center pt-4">
          <button @click="confirmDeliveryType" 
                  class="px-6 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors">
            Continuar
          </button>
        </div>
      </div>
      
      <!-- PASO 3: SELECCIÓN DE TRANSPORTISTA (después de completar dirección) -->
      <div v-if="showCarrierSelection" class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-heading text-lg font-medium text-gray-900">Elegir transportista</h3>
          <button @click="showAddressForm = true; showCarrierSelection = false" class="text-sm text-blue-600 hover:underline">
            ← Volver a dirección
          </button>
        </div>
        
        <!-- Loading state -->
        <div v-if="isLoadingQuotes" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p class="mt-2 text-sm text-gray-600">Calculando costos de envío...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="quotesError" class="text-center py-8">
          <p class="text-sm text-red-600 mb-4">{{ quotesError }}</p>
          <button @click="loadShippingQuotes" class="text-sm text-blue-600 hover:underline">
            Reintentar
          </button>
        </div>
        
        <!-- Transportistas disponibles -->
        <div v-else class="space-y-3">
          <!-- Andreani -->
          <div class="provider-option-compact flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
               :class="selectedCarrier === 'envio_andreani' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
               @click="selectCarrier('envio_andreani')">
            <div class="flex items-center">
              <div class="w-8 h-8 mr-3 flex items-center justify-center bg-gray-100 rounded text-lg">🚚</div>
              <div>
                <h4 class="text-sm font-medium text-gray-900">Andreani</h4>
                <p class="text-xs text-gray-500">3-5 días hábiles</p>
              </div>
            </div>
            <span class="text-sm font-medium text-gray-900">
              ${{ deliveryCosts['envio_andreani']?.toLocaleString() || '500' }}
            </span>
          </div>
          
          <!-- Correo Argentino -->
          <div class="provider-option-compact flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
               :class="selectedCarrier === 'envio_correo' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
               @click="selectCarrier('envio_correo')">
            <div class="flex items-center">
              <div class="w-8 h-8 mr-3 flex items-center justify-center bg-gray-100 rounded text-lg">📦</div>
              <div>
                <h4 class="text-sm font-medium text-gray-900">Correo Argentino</h4>
                <p class="text-xs text-gray-500">5-8 días hábiles</p>
              </div>
            </div>
            <span class="text-sm font-medium text-gray-900">
              ${{ deliveryCosts['envio_correo']?.toLocaleString() || '400' }}
            </span>
          </div>
          
          <!-- OCA -->
          <div class="provider-option-compact flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
               :class="selectedCarrier === 'envio_oca' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
               @click="selectCarrier('envio_oca')">
            <div class="flex items-center">
              <div class="w-8 h-8 mr-3 flex items-center justify-center bg-gray-100 rounded text-lg">🚚</div>
              <div>
                <h4 class="text-sm font-medium text-gray-900">OCA</h4>
                <p class="text-xs text-gray-500">4-6 días hábiles</p>
              </div>
            </div>
            <span class="text-sm font-medium text-gray-900">
              ${{ deliveryCosts['envio_oca']?.toLocaleString() || '450' }}
            </span>
          </div>
          
          <!-- Cotización personalizada -->
          <div class="provider-option-compact flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
               :class="selectedCarrier === 'cotizacion_personalizada' ? 'border-gray-800 bg-gray-50' : 'border-gray-200'"
               @click="selectCarrier('cotizacion_personalizada')">
            <div class="flex items-center">
              <div class="w-8 h-8 mr-3 flex items-center justify-center bg-gray-100 rounded text-lg">📞</div>
              <div>
                <h4 class="text-sm font-medium text-gray-900">Cotización personalizada</h4>
                <p class="text-xs text-gray-500">Te contactamos para cotizar</p>
                <p class="text-xs text-blue-600 mt-1">
                  📱 WhatsApp: +54 9 11 1234-5678
                </p>
              </div>
            </div>
            <span class="text-sm font-medium text-blue-600">A cotizar</span>
          </div>
        </div>
        
        <!-- Botón confirmar transportista -->
        <div v-if="selectedCarrier" class="text-center pt-4">
          <button @click="confirmCarrierSelection" 
                  class="px-6 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors">
            Confirmar {{ getCarrierDisplayName(selectedCarrier) }}
          </button>
        </div>
      </div>
    </div>

    <!-- 2. DIRECCIÓN DE ENVÍO (PASO 2 - Solo para envío a domicilio) -->
    <div v-if="showAddressForm" class="bg-white shadow rounded-lg p-6">
      <h3 class="font-heading text-lg font-medium text-gray-900 mb-4">Dirección de envío</h3>
      
      <div class="space-y-4">
        <div>
          <AddressAutocomplete
            :model-value="address"
            @update:model-value="$emit('update:address', $event)"
            input-id="address"
            :country-code="country"
            required
            @address-selected="onAddressSelected"
          />
        </div>
        
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label for="city" class="font-body block text-sm font-medium text-body-text">Ciudad</label>
            <input
              :value="city"
              @input="$emit('update:city', ($event.target as HTMLInputElement).value)"
              type="text"
              id="city"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            >
          </div>
          
          <div>
            <label for="postalCode" class="font-body block text-sm font-medium text-body-text">Código Postal</label>
            <input
              :value="postalCode"
              @input="$emit('update:postalCode', ($event.target as HTMLInputElement).value)"
              type="text"
              id="postalCode"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            >
          </div>
        </div>
        
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label for="province" class="font-body block text-sm font-medium text-body-text">Provincia</label>
            <input
              :value="province"
              @input="$emit('update:province', ($event.target as HTMLInputElement).value)"
              type="text"
              id="province"
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
              placeholder="Buenos Aires"
            >
          </div>
          
          <div>
            <label for="country" class="font-body block text-sm font-medium text-body-text">País</label>
            <select
              :value="country"
              @change="$emit('update:country', ($event.target as HTMLSelectElement).value)"
              id="country"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            >
              <option class="font-body" value="AR">Argentina</option>
              <option class="font-body" value="UY">Uruguay</option>
              <option class="font-body" value="CL">Chile</option>
            </select>
          </div>
        </div>
        
        <div>
          <label for="addressReference" class="font-body block text-sm font-medium text-body-text">Referencias de dirección (opcional)</label>
          <input
            :value="addressReference"
            @input="$emit('update:addressReference', ($event.target as HTMLInputElement).value)"
            type="text"
            id="addressReference"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            placeholder="Entre calles, piso, depto, etc."
          >
        </div>
        
        <div>
          <label for="deliveryNotes" class="font-body block text-sm font-medium text-body-text">Notas para la entrega (opcional)</label>
          <textarea
            :value="deliveryNotes"
            @input="$emit('update:deliveryNotes', ($event.target as HTMLTextAreaElement).value)"
            id="deliveryNotes"
            rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            placeholder="Horarios de entrega, portero eléctrico, etc."
          ></textarea>
        </div>
        
        <div>
          <label for="preferredDeliveryTime" class="font-body block text-sm font-medium text-body-text">Horario preferido de entrega</label>
          <select
            :value="preferredDeliveryTime"
            @change="$emit('update:preferredDeliveryTime', ($event.target as HTMLSelectElement).value)"
            id="preferredDeliveryTime"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
          >
            <option class="font-body" value="cualquiera">Cualquier horario</option>
            <option class="font-body" value="mañana">Mañana (9:00 - 13:00)</option>
            <option class="font-body" value="tarde">Tarde (14:00 - 18:00)</option>
            <option class="font-body" value="noche">Noche (18:00 - 21:00)</option>
          </select>
        </div>
        
        <!-- Botón para continuar con selección de transportista -->
        <div class="text-center pt-6">
          <button @click="completeAddressAndShowCarriers" 
                  :disabled="!isAddressValid"
                  :class="[
                    'px-6 py-2 rounded-md transition-colors',
                    isAddressValid 
                      ? 'bg-gray-800 text-white hover:bg-gray-700' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  ]">
            Continuar - Elegir Transportista
          </button>
        </div>
      </div>
    </div>

    <!-- INFORMACIÓN DE RETIRO LOCAL -->
    <div v-if="deliveryType === 'retiro_local' && !showDeliveryTypeSelection" class="bg-white shadow rounded-lg p-6">
      <div class="p-4 border border-blue-200 rounded-lg bg-blue-50">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="ml-3">
            <h4 class="text-sm font-medium text-blue-900">Coordinar Retiro</h4>
            <p class="mt-1 text-sm text-blue-700">
              Después de completar tu compra, te contactaremos por WhatsApp para coordinar el horario de retiro.
            </p>
            <div class="mt-2 text-sm text-blue-700">
              <strong>Contacto:</strong> +54 9 11 1234-5678<br>
              <strong>Dirección:</strong> Av. Ejemplo 123, CABA
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. INFORMACIÓN DE COTIZACIÓN PERSONALIZADA -->
    <div v-if="!showProviderSelection && selectedDeliveryMethod === 'cotizacion_personalizada'" class="bg-white shadow rounded-lg p-6">
      <div class="p-4 border border-blue-200 rounded-lg bg-blue-50">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          <div class="ml-3">
            <h4 class="text-sm font-medium text-blue-900">Cotización Personalizada</h4>
            <p class="mt-1 text-sm text-blue-700">
              Te contactaremos por WhatsApp para cotizar el envío según tu ubicación específica y las características del pedido.
            </p>
            <div class="mt-3 space-y-2">
              <div class="text-sm text-blue-700">
                <strong>¿Cómo funciona?</strong>
              </div>
              <ul class="text-sm text-blue-700 list-disc list-inside space-y-1">
                <li>Analizamos tu ubicación y el pedido</li>
                <li>Te contactamos con la mejor opción de envío</li>
                <li>Negociamos el mejor precio según la zona</li>
                <li>Coordinamos fecha y horario de entrega</li>
              </ul>
              <div class="mt-3 text-sm text-blue-700">
                <strong>Contacto:</strong> +54 9 11 1234-5678<br>
                <strong>Horario:</strong> Lunes a Viernes 9:00 - 18:00
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. BOTÓN CONTINUAR AL PAGO -->
    <div v-if="!showProviderSelection && isDeliveryInfoComplete" class="bg-white shadow rounded-lg p-6">
      <div class="text-center">
        <div class="mb-4">
          <div class="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3">
            <svg class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h3 class="font-heading text-lg font-medium text-gray-900 mb-2">Información de entrega completa</h3>
          <p class="font-body text-sm text-gray-600 mb-4">Ya puedes continuar con el método de pago</p>
        </div>
        <button
          type="button"
          @click="$emit('continue')"
          class="w-full sm:w-auto inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-black hover:bg-gray-800 transition-colors"
        >
          <span class="text-white">Continuar al pago</span>
          <svg class="ml-2 -mr-1 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { shippingQuotesApi } from '../../config/api'
import AddressAutocomplete from '../forms/AddressAutocomplete.vue'
import type { ParsedAddress } from '../../composables/useAddressAutocomplete'

// Debounce utility
function debounce<T extends (...args: any[]) => any>(func: T, wait: number): T {
  let timeout: NodeJS.Timeout | null = null
  return ((...args: any[]) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }) as T
}

interface Props {
  selectedDeliveryMethod: string
  address: string
  city: string
  postalCode: string
  province: string
  country: string
  addressReference: string
  deliveryNotes: string
  preferredDeliveryTime: string
  totalWeightKg?: number
}

interface ShippingOption {
  carrier: string
  name: string
  price: number
  currency: string
  estimated_days?: number
  estimated_delivery_text: string
  service_type?: string
  has_error: boolean
  error_message?: string
}

const props = withDefaults(defineProps<Props>(), {
  totalWeightKg: 1.0
})

const emit = defineEmits<{
  'update:selectedDeliveryMethod': [value: string]
  'update:address': [value: string]
  'update:city': [value: string]
  'update:postalCode': [value: string]
  'update:province': [value: string]
  'update:country': [value: string]
  'update:addressReference': [value: string]
  'update:deliveryNotes': [value: string]
  'update:preferredDeliveryTime': [value: string]
  'delivery-method-changed': [data: { method: string; cost: number }]
  'continue': []
}>()

// State
const shippingOptions = ref<ShippingOption[]>([])
const isLoadingQuotes = ref(false)
const quotesError = ref<string | null>(null)

// Nuevo flujo de estados
const deliveryType = ref<string>('')                    // 'retiro_local' o 'envio_domicilio'
const selectedCarrier = ref<string>('')                 // transportista seleccionado
const showDeliveryTypeSelection = ref(true)             // Paso 1: elegir tipo
const showAddressForm = ref(false)                      // Paso 2: datos de contacto
const showCarrierSelection = ref(false)                 // Paso 3: elegir transportista
const addressCompleted = ref(false)                     // Si completó datos de contacto

// Estados legacy (mantener compatibilidad)
const showProviderSelection = ref(false)     
const providerSelected = ref(false)

// Fallback delivery costs
const fallbackDeliveryCosts = {
  'envio_andreani': 500,
  'envio_correo': 400,
  'envio_oca': 450,
  'retiro_local': 0,
  'cotizacion_personalizada': 0
}

// Computed property for current delivery costs
const deliveryCosts = computed(() => {
  if (shippingOptions.value.length > 0) {
    const costs: Record<string, number> = { 'retiro_local': 0, 'cotizacion_personalizada': 0 }
    shippingOptions.value.forEach(option => {
      // Map backend carrier names to frontend method names
      const carrierMapping: Record<string, string> = {
        'oca': 'envio_oca',
        'andreani': 'envio_andreani', 
        'correo_argentino': 'envio_correo'
      }
      const frontendMethod = carrierMapping[option.carrier] || `envio_${option.carrier}`
      costs[frontendMethod] = option.price
    })
    return costs
  } else {
    return fallbackDeliveryCosts
  }
})

// Check if delivery info is complete
const isDeliveryInfoComplete = computed(() => {
  // For retiro local, only need delivery type selected
  if (deliveryType.value === 'retiro_local') return true
  
  // For envio domicilio, need address completed AND carrier selected
  if (deliveryType.value === 'envio_domicilio') {
    return addressCompleted.value && selectedCarrier.value !== ''
  }
  
  return false
})

// Método para confirmar selección de proveedor
const confirmSelection = () => {
  showProviderSelection.value = false
  providerSelected.value = true
}

// Método para cambiar proveedor (volver al paso 1)
const changeProvider = () => {
  showProviderSelection.value = true
  providerSelected.value = false
  emit('update:selectedDeliveryMethod', '')
}

// Métodos helper para mostrar información del proveedor
const getProviderDisplayName = (method: string): string => {
  const names: Record<string, string> = {
    'envio_andreani': 'Andreani',
    'envio_correo': 'Correo Argentino',
    'envio_oca': 'OCA', 
    'retiro_local': 'Retiro en Local',
    'cotizacion_personalizada': 'Cotización Personalizada'
  }
  return names[method] || method
}

const getProviderIcon = (method: string): string => {
  const icons: Record<string, string> = {
    'envio_andreani': '📦',
    'envio_correo': '📮', 
    'envio_oca': '🚚',
    'retiro_local': '🏪',
    'cotizacion_personalizada': '📞'
  }
  return icons[method] || '📦'
}

const getProviderDescription = (method: string): string => {
  const descriptions: Record<string, string> = {
    'envio_andreani': 'Entrega a domicilio en 3-5 días hábiles',
    'envio_correo': 'Entrega a domicilio en 5-8 días hábiles',
    'envio_oca': 'Entrega a domicilio en 4-6 días hábiles',
    'retiro_local': 'Coordinar horario de retiro con el vendedor',
    'cotizacion_personalizada': 'Te contactamos para cotizar según tu ubicación'
  }
  return descriptions[method] || ''
}

const getProviderPrice = (method: string): string => {
  const cost = (deliveryCosts.value as Record<string, number>)[method] || 0
  if (method === 'cotizacion_personalizada') {
    return 'A cotizar'
  }
  return cost === 0 ? 'Gratis' : `$${cost.toLocaleString()}`
}

// Nuevos métodos para el flujo
const selectDeliveryType = (type: string) => {
  deliveryType.value = type
}

const confirmDeliveryType = () => {
  if (deliveryType.value === 'retiro_local') {
    // Para retiro local, emitir directamente y completar
    emit('update:selectedDeliveryMethod', 'retiro_local')
    emit('delivery-method-changed', { method: 'retiro_local', cost: 0 })
    showDeliveryTypeSelection.value = false
  } else if (deliveryType.value === 'envio_domicilio') {
    // Para envío a domicilio, mostrar formulario de dirección
    showDeliveryTypeSelection.value = false
    showAddressForm.value = true
  }
}

const selectCarrier = (carrier: string) => {
  selectedCarrier.value = carrier
}

const confirmCarrierSelection = () => {
  // Emitir el transportista seleccionado
  emit('update:selectedDeliveryMethod', selectedCarrier.value)
  const cost = (deliveryCosts.value as Record<string, number>)[selectedCarrier.value] || 0
  emit('delivery-method-changed', { method: selectedCarrier.value, cost })
  showCarrierSelection.value = false
}

const getCarrierDisplayName = (carrier: string): string => {
  const names: Record<string, string> = {
    'envio_andreani': 'Andreani',
    'envio_correo': 'Correo Argentino',
    'envio_oca': 'OCA',
    'cotizacion_personalizada': 'Cotización Personalizada'
  }
  return names[carrier] || carrier
}

// Método legacy (mantener compatibilidad)
const selectDeliveryMethod = (method: string) => {
  emit('update:selectedDeliveryMethod', method)
  const cost = (deliveryCosts.value as Record<string, number>)[method] || 0
  emit('delivery-method-changed', { method, cost })
}

const getDeliveryCost = () => {
  return (deliveryCosts.value as Record<string, number>)[props.selectedDeliveryMethod] || 0
}

// Validar si la dirección está completa
const isAddressValid = computed(() => {
  return props.address.trim() && 
         props.city.trim() && 
         props.postalCode.trim()
})

// Completar dirección y mostrar transportistas
const completeAddressAndShowCarriers = () => {
  if (isAddressValid.value) {
    addressCompleted.value = true
    showAddressForm.value = false
    showCarrierSelection.value = true
    
    // Cargar cotizaciones si hay código postal
    if (props.postalCode && props.postalCode.trim().length >= 4) {
      loadShippingQuotes()
    }
  }
}

const onAddressSelected = (parsedAddress: ParsedAddress) => {
  emit('update:address', parsedAddress.street)
  emit('update:city', parsedAddress.city)
  emit('update:postalCode', parsedAddress.postalCode)
  emit('update:province', parsedAddress.province)
  emit('update:country', parsedAddress.country)
}

// Function to load shipping quotes from API
const loadShippingQuotes = async () => {
  if (!props.postalCode) {
    return
  }

  // Don't load quotes for very short postal codes
  if (props.postalCode.trim().length < 4) {
    return
  }

  isLoadingQuotes.value = true
  quotesError.value = null

  try {

    const response = await shippingQuotesApi.getShippingQuotes({
      postal_code: props.postalCode,
      city: props.city,
      province: props.province,
      total_weight_kg: props.totalWeightKg || 1.0,
      include_fallback: true
    })

    if (response.success && response.options) {
      shippingOptions.value = response.options

      // Update cost for current method if available
      const carrierMapping: Record<string, string> = {
        'oca': 'envio_oca',
        'andreani': 'envio_andreani', 
        'correo_argentino': 'envio_correo'
      }
      const currentOption = response.options.find((opt: ShippingOption) => {
        const frontendMethod = carrierMapping[opt.carrier] || `envio_${opt.carrier}`
        return props.selectedDeliveryMethod === frontendMethod
      })
      if (currentOption) {
        emit('delivery-method-changed', { 
          method: props.selectedDeliveryMethod, 
          cost: currentOption.price 
        })
      }

      // Only show error message if ALL options have errors AND it's not just incomplete postal code
      const allHaveErrors = response.options.every((opt: ShippingOption) => opt.has_error)
      const hasIncompletePostalCodeError = response.options.some((opt: ShippingOption) => 
        opt.error_message?.includes('Código postal incompleto')
      )
      
      if (allHaveErrors && !hasIncompletePostalCodeError && !response.api_available) {
        quotesError.value = response.message || 'Usando precios estimados'
      }
    } else {
      throw new Error('Invalid response format')
    }

  } catch (error) {
    quotesError.value = 'Error al cargar cotizaciones, usando precios estimados'
    shippingOptions.value = []
  } finally {
    isLoadingQuotes.value = false
  }
}

// Helper function to get shipping option for display
const getShippingOption = (carrier: string): ShippingOption | null => {
  return shippingOptions.value.find(opt => opt.carrier === carrier) || null
}

// Create debounced version of loadShippingQuotes
const debouncedLoadShippingQuotes = debounce(loadShippingQuotes, 800)

// Watch for postal code changes to trigger new quotes
watch(() => [props.postalCode, props.totalWeightKg], () => {
  if (props.postalCode && props.postalCode.trim().length >= 4) {
    debouncedLoadShippingQuotes()
  }
}, { immediate: false })

// Load quotes on mount if postal code is available
onMounted(() => {
  if (props.postalCode) {
    loadShippingQuotes()
  }
  
  // Emit initial delivery method cost
  const cost = (deliveryCosts.value as Record<string, number>)[props.selectedDeliveryMethod] || 0
  emit('delivery-method-changed', { method: props.selectedDeliveryMethod, cost })
})
</script>

<style scoped>
.provider-option-compact {
  @apply transition-all duration-200;
}

.provider-option-compact:hover {
  @apply bg-gray-50 border-gray-300;
}
</style>