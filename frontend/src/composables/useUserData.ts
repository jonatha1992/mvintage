import { ref, computed } from 'vue'
import { customersApi } from '../config/api'
import { useAuthStore } from '../store/auth'
import type { Customer } from '../types/users/user.types'

export function useUserData() {
  const authStore = useAuthStore()

  const customerData = ref<Customer | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasCustomerData = computed(() => customerData.value !== null)

  /**
   * Carga automÃ¡ticamente los datos del customer si el usuario estÃ¡ autenticado
   */
  const loadCustomerData = async (): Promise<Customer | null> => {
    // Solo cargar si el usuario estÃ¡ autenticado
    if (!authStore.isAuthenticated) {
      customerData.value = null
      return null
    }

    loading.value = true
    error.value = null

    try {
      const data = await customersApi.getMyCustomerData()
      customerData.value = data
      return data
    } catch (err: any) {
      // 404 es normal para usuarios sin compras anteriores
      if (err?.response?.status === 404) {
        customerData.value = null
        error.value = null
      } else {
        error.value = 'Error al cargar los datos del usuario'
        customerData.value = null
      }
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Limpia los datos del customer
   */
  const clearCustomerData = () => {
    customerData.value = null
    error.value = null
    loading.value = false
  }

  /**
   * Convierte los datos del customer a formato para el formulario de checkout
   */
  const getCheckoutFormData = () => {
    if (!customerData.value) return {}

    return {
      firstName: customerData.value.first_name || '',
      lastName: customerData.value.last_name || '',
      email: customerData.value.email || '',
      phone: customerData.value.phone || '',
      address: customerData.value.address || '',
      city: customerData.value.city || '',
      postalCode: customerData.value.postal_code || '',
      province: customerData.value.province || '',
      country: customerData.value.country || 'AR',
      addressReference: customerData.value.address_reference || '',
      deliveryNotes: customerData.value.delivery_notes || '',
      preferredDeliveryTime: customerData.value.preferred_delivery_time || '',
      phoneCountryCode: 'AR' // Asume Argentina por defecto
    }
  }

  return {
    // State
    customerData: readonly(customerData),
    loading: readonly(loading),
    error: readonly(error),

    // Computed
    hasCustomerData,

    // Methods
    loadCustomerData,
    clearCustomerData,
    getCheckoutFormData
  }
}

// Funcin auxiliar para readonly
function readonly<T>(ref: any) {
  return ref
}