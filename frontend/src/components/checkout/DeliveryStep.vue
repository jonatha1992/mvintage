<template>
  <div class="space-y-6">
    

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
      
    </div>
    
    <!-- PASO 2: DIRECCIÓN DE ENVÍO (Solo para envío a domicilio) -->
    <div v-if="showAddressForm" class="bg-white shadow rounded-lg p-4">
      <h3 class="font-heading text-lg font-medium text-gray-900 mb-3">Dirección de envío</h3>
      
      <div class="space-y-3">
        <!-- Datos de contacto -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label for="firstName" class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              :value="firstName"
              @input="$emit('update:firstName', ($event.target as HTMLInputElement).value)"
              id="firstName"
              placeholder="Nombre"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
              required
            />
          </div>
          <div>
            <label for="lastName" class="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
            <input
              type="text"
              :value="lastName"
              @input="$emit('update:lastName', ($event.target as HTMLInputElement).value)"
              id="lastName"
              placeholder="Apellido"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
              required
            />
          </div>
        </div>

        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
          <input
            type="tel"
            :value="phone"
            @input="$emit('update:phone', ($event.target as HTMLInputElement).value)"
            id="phone"
            placeholder="Ej: 11 1234-5678"
            class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            required
          />
        </div>

        <!-- Código Postal con ciudad autocompletada -->
        <div class="flex items-center space-x-2 p-3 border border-gray-300 rounded-md bg-gray-50">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-700">
              Código Postal {{ postalCode || '____' }}
            </div>
            <div class="text-sm text-gray-500">
              {{ city || 'Ciudad' }}
            </div>
          </div>
          <button 
            @click="showPostalCodeEdit = true"
            class="text-sm text-blue-600 hover:underline"
          >
            Cambiar
          </button>
        </div>

        <!-- Modal para editar código postal -->
        <div v-if="showPostalCodeEdit" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white p-6 rounded-lg max-w-sm w-full mx-4">
            <h3 class="text-lg font-medium mb-4">Código Postal</h3>
            <input
              type="text"
              :value="postalCode"
              @input="handlePostalCodeChange"
              placeholder="Ej: 1804"
              maxlength="6"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black mb-4"
              required
            />
            <div class="flex justify-end space-x-2">
              <button 
                @click="showPostalCodeEdit = false"
                class="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button 
                @click="showPostalCodeEdit = false"
                class="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>

        <!-- Dirección separada en campos -->
        <div>
          <label for="street" class="block text-sm font-medium text-gray-700 mb-1">Calle</label>
          <input
            type="text"
            :value="street"
            @input="$emit('update:street', ($event.target as HTMLInputElement).value)"
            id="street"
            placeholder="Ej: Av. Corrientes"
            class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            required
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="streetNumber" class="block text-sm font-medium text-gray-700 mb-1">Número</label>
            <input
              type="text"
              :value="streetNumber"
              @input="$emit('update:streetNumber', ($event.target as HTMLInputElement).value)"
              id="streetNumber"
              placeholder="1234"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
              required
            />
          </div>
          <div class="flex items-center">
            <input
              type="checkbox"
              id="noNumber"
              class="mr-2"
            />
            <label for="noNumber" class="text-sm text-gray-600">Sin número</label>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label for="apartment" class="block text-sm font-medium text-gray-700 mb-1">Departamento (opcional)</label>
            <input
              type="text"
              :value="apartment"
              @input="$emit('update:apartment', ($event.target as HTMLInputElement).value)"
              id="apartment"
              placeholder="Ej: 4B"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            />
          </div>
          <div>
            <label for="neighborhood" class="block text-sm font-medium text-gray-700 mb-1">Barrio (opcional)</label>
            <input
              type="text"
              :value="neighborhood"
              @input="$emit('update:neighborhood', ($event.target as HTMLInputElement).value)"
              id="neighborhood"
              placeholder="Ej: Microcentro"
              class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black"
            />
          </div>
        </div>

        <div>
          <label for="city" class="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
          <input
            type="text"
            :value="city"
            @input="$emit('update:city', ($event.target as HTMLInputElement).value)"
            id="city"
            class="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:border-black focus:ring-black bg-gray-50"
            readonly
          />
        </div>
        
        <!-- Botón para continuar con selección de transportista -->
        <div class="text-center pt-4">
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

    <!-- PASO 3: SELECCIÓN DE TRANSPORTISTA (después de completar dirección) -->
    <div v-if="showCarrierSelection" class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-heading text-lg font-medium text-gray-900">Elegir transportista</h3>
        <button @click="showAddressForm = true; showCarrierSelection = false" class="text-sm text-blue-600 hover:underline">
          ← Volver a dirección
        </button>
      </div>
      
      <!-- Error state -->
      <div v-if="quotesError" class="text-center py-8">
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
            ${{ (deliveryCosts['envio_andreani'] || 500).toLocaleString('es-AR') }}
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
            ${{ (deliveryCosts['envio_correo'] || 400).toLocaleString('es-AR') }}
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
            ${{ (deliveryCosts['envio_oca'] || 450).toLocaleString('es-AR') }}
          </span>
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
            <p class="mt-2 text-sm text-blue-700">
              <strong>Dirección:</strong> Av. Corrientes 1234, CABA<br>
              <strong>Horarios:</strong> Lunes a Viernes 10:00 - 18:00, Sábados 10:00 - 14:00
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- BOTÓN CONTINUAR AL PAGO -->
    <Transition
      enter-active-class="transition-all duration-500 ease-out"
      enter-from-class="opacity-0 transform translate-y-4 scale-95"
      enter-to-class="opacity-100 transform translate-y-0 scale-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="opacity-100 transform translate-y-0 scale-100"
      leave-to-class="opacity-0 transform translate-y-4 scale-95"
    >
      <div v-if="isDeliveryInfoComplete" class="bg-white shadow rounded-lg p-6">
        <div class="text-center">
          <div class="mb-4">
            <div class="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3 animate-bounce-once">
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
            class="w-full sm:w-auto inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-black hover:bg-gray-800 transition-all duration-200 hover:scale-105 active:scale-95"
          >
            <span class="text-white">Continuar al pago</span>
            <svg class="ml-2 -mr-1 w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { shippingQuotesApi } from '../../config/api'
import AddressAutocomplete from '../forms/AddressAutocomplete.vue'
import type { ShippingQuoteOption } from '../../types/orders/shipping.types'
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
  streetNumber: string
  fullAddress: string
  city: string
  postalCode: string
  province: string
  country: string
  addressReference: string
  deliveryNotes: string
  preferredDeliveryTime: string
  totalWeightKg: number
  // Nuevos campos siguiendo patrón Bohme
  firstName: string
  lastName: string
  phone: string
  street: string
  apartment: string
  neighborhood: string
}

const props = withDefaults(defineProps<Props>(), {
  selectedDeliveryMethod: '',
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
  totalWeightKg: 0.5
})

interface ShippingOption {
  carrier: string
  service: string
  price: number
  estimatedDays: string
  description: string
}

const emit = defineEmits<{
  'update:selectedDeliveryMethod': [value: string]
  'update:address': [value: string]
  'update:streetNumber': [value: string]
  'update:fullAddress': [value: string]
  'update:city': [value: string]
  'update:postalCode': [value: string]
  'update:province': [value: string]
  'update:country': [value: string]
  'update:addressReference': [value: string]
  'update:deliveryNotes': [value: string]
  'update:preferredDeliveryTime': [value: string]
  'update:firstName': [value: string]
  'update:lastName': [value: string]
  'update:phone': [value: string]
  'update:street': [value: string]
  'update:apartment': [value: string]
  'update:neighborhood': [value: string]
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
const showPostalCodeEdit = ref(false)                   // Modal para editar código postal

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
        'correoArgentino': 'envio_correo'
      }
      const frontendMethod = carrierMapping[option.carrier] || option.carrier
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
  if (deliveryType.value === 'retiro_local') {
    return true
  }
  
  // For envio domicilio, need address completed AND carrier selected
  if (deliveryType.value === 'envio_domicilio') {
    const isComplete = addressCompleted.value && selectedCarrier.value !== ''
    return isComplete
  }
  
  return false
})

// Validar si la dirección está completa
const isAddressValid = computed(() => {
  const isValid = props.street.trim() && 
         props.city.trim() && 
         props.postalCode.trim()
  
  return isValid
})

// Nuevos métodos para el flujo
const selectDeliveryType = (type: string) => {
  deliveryType.value = type
  // Avanzar automáticamente al seleccionar tipo
  confirmDeliveryType()
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
  // Confirmar automáticamente al seleccionar transportista
  confirmCarrierSelection()
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
  }
  return names[carrier] || carrier
}

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
  if (!props.postalCode || props.postalCode.trim().length < 4) {
    return
  }

  isLoadingQuotes.value = true
  quotesError.value = null
  
  try {
    
    const response = await shippingQuotesApi.getShippingQuotes({
      postal_code: props.postalCode,
      total_weight_kg: props.totalWeightKg,
      city: props.city || undefined,
      province: props.province || undefined
    })
    
    if (response.success && response.options) {
      shippingOptions.value = response.options.map((quote: ShippingQuoteOption) => ({
        carrier: quote.carrier,
        service: quote.service_type || quote.name,
        price: quote.price,
        estimatedDays: quote.estimated_days,
        description: quote.estimated_delivery_text
      }))
      
      // Solo mostrar error si hay problemas reales, no por precios estimados normales
      if (response.message && !response.api_available) {
        quotesError.value = response.message
      }
    } else {
      throw new Error(response.message || 'Error al obtener cotizaciones')
    }
  } catch (error: any) {
    // Mejorar el mensaje de error para ser más claro
    if (error.message?.includes('precios estimados')) {
      quotesError.value = 'Servicio de cotización temporalmente no disponible. Mostrando precios estimados.'
    } else {
      quotesError.value = 'Servicio de cotización no disponible. Usando precios estimados.'
    }
  } finally {
    isLoadingQuotes.value = false
  }
}

// Create debounced version of loadShippingQuotes
const debouncedLoadShippingQuotes = debounce(loadShippingQuotes, 800)

// Watch for postal code changes to trigger new quotes
watch(() => [props.postalCode, props.totalWeightKg], () => {
  if (props.postalCode && props.postalCode.trim().length >= 4) {
    debouncedLoadShippingQuotes()
  }
}, { immediate: false })

// Función para manejar cambios en código postal
const handlePostalCodeChange = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  emit('update:postalCode', value)
  
  // Auto-completar ciudad y provincia basado en código postal argentino
  if (value.length >= 4) {
    // Lógica básica para algunas ciudades principales
    const postalCodeMap: Record<string, { city: string; province: string }> = {
      '1000': { city: 'Buenos Aires', province: 'Ciudad Autónoma de Buenos Aires' },
      '1001': { city: 'Buenos Aires', province: 'Ciudad Autónoma de Buenos Aires' },
      '1804': { city: 'Ezeiza', province: 'Buenos Aires' },
      '1759': { city: 'González Catán', province: 'Buenos Aires' },
      '1900': { city: 'La Plata', province: 'Buenos Aires' },
      '2000': { city: 'Rosario', province: 'Santa Fe' },
      '5000': { city: 'Córdoba', province: 'Córdoba' },
    }
    
    const location = postalCodeMap[value]
    if (location) {
      emit('update:city', location.city)
      emit('update:province', location.province)
    }
  }
}

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

@keyframes bounce-once {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0,0,0);
  }
  40%, 43% {
    transform: translate3d(0,-8px,0);
  }
  70% {
    transform: translate3d(0,-4px,0);
  }
  90% {
    transform: translate3d(0,-2px,0);
  }
}

.animate-bounce-once {
  animation: bounce-once 1s ease-out;
}
</style>
