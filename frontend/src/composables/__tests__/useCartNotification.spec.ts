import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useCartNotification } from '../useCartNotification'
import type { Product } from '../../types/products'

const product = { id: 1, name: 'Blusa Vela', price: 33000, is_unique: true, stock: 2, images: [] } as unknown as Product

describe('aviso del carrito', () => {
  it('muestra errores sin anunciar una incorporación exitosa', () => {
    const notice = useCartNotification()
    notice.showError('No hay stock disponible')
    expect(notice.errorMessage.value).toBe('No hay stock disponible')
    expect(notice.productData.value).toBeNull()
    expect(notice.isNotificationVisible.value).toBe(true)
  })
  beforeEach(() => { vi.useFakeTimers(); useCartNotification().hideNotification() })
  afterEach(() => { useCartNotification().hideNotification(); vi.useRealTimers() })

  it('conserva talle y color de prendas únicas y dura tres segundos', () => {
    const notice = useCartNotification()
    notice.showNotification(product, 1, { color: { id: 1, name: 'Beige' }, size: { id: 2, name: 'M' } })
    expect(notice.productData.value?.variant).toEqual({ color: 'Beige', size: 'M' })
    vi.advanceTimersByTime(2999)
    expect(notice.isNotificationVisible.value).toBe(true)
    vi.advanceTimersByTime(1)
    expect(notice.isNotificationVisible.value).toBe(false)
  })
})
