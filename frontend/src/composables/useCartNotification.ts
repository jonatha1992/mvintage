import { ref } from 'vue'
import type { Product, VariantOption } from '../types/products'

interface NotificationProductData {
  image: string
  name: string
  variant: { color: string; size: string }
}

const isNotificationVisible = ref(false)
const productData = ref<NotificationProductData | null>(null)
const errorMessage = ref('')
const additionId = ref(0)
let autoHideTimer: ReturnType<typeof setTimeout> | undefined

export function useCartNotification() {
  const pauseDismissal = () => {
    clearTimeout(autoHideTimer)
    autoHideTimer = undefined
  }
  const hideNotification = () => {
    pauseDismissal()
    isNotificationVisible.value = false
  }
  const resumeDismissal = () => {
    pauseDismissal()
    autoHideTimer = setTimeout(hideNotification, 3000)
  }
  const showNotification = (
    product: Product,
    _quantity: number,
    selection?: { color?: VariantOption; size?: VariantOption }
  ) => {
    errorMessage.value = ''
    productData.value = {
      image: product.images?.[0]?.image_url || '/logo_redondo.jpg',
      name: product.name,
      variant: { color: selection?.color?.name || 'Único', size: selection?.size?.name || 'Único' }
    }
    additionId.value++
    isNotificationVisible.value = true
    resumeDismissal()
  }
  const showError = (message: string) => {
    productData.value = null
    errorMessage.value = message
    isNotificationVisible.value = true
    resumeDismissal()
  }
  return { isNotificationVisible, productData, errorMessage, additionId, showNotification, showError,
    hideNotification, pauseDismissal, resumeDismissal }
}
