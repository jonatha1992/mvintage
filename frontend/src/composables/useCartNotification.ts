import { ref } from 'vue'
import type {
  Product,
  ProductVariant,
  VariantOption as Color,
  VariantOption as Size
} from '../types/products'

interface NotificationProductData {
  image: string
  name: string
  quantity: number
  price: number
  hasDiscount: boolean
  category?: string
  variant?: {
    color: string
    size: string
  }
}

const isNotificationVisible = ref(false)
const productData = ref<NotificationProductData | null>(null)
let autoHideTimer: number | null = null

export function useCartNotification() {
  const showNotification = (
    product: Product,
    quantity: number,
    variantInfo?: { variant: ProductVariant; color: Color; size: Size }
  ) => {
    // Preparar datos del producto para la notificación
    const price = product.has_discount && product.discounted_price
      ? product.discounted_price
      : product.price
    const image = product.images && product.images.length > 0
      ? product.images[0].image_url
      : '/placeholder-image.jpg'

    productData.value = {
      image,
      name: product.name,
      quantity,
      price: price || 0,
      hasDiscount: product.has_discount || false,
      category: product.categoria || undefined,
      variant: variantInfo ? {
        color: variantInfo.color.name,
        size: variantInfo.size.name
      } : undefined
    }

    isNotificationVisible.value = true

    // Auto hide después de 3 segundos
    if (autoHideTimer) clearTimeout(autoHideTimer)
    autoHideTimer = window.setTimeout(() => {
      hideNotification()
    }, 3000)
  }

  const hideNotification = () => {
    isNotificationVisible.value = false
    if (autoHideTimer) {
      clearTimeout(autoHideTimer)
      autoHideTimer = null
    }
  }

  return {
    isNotificationVisible,
    productData,
    showNotification,
    hideNotification
  }
}