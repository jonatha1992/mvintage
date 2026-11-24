import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useCartStore } from '../cart'
import { useCartNotification } from '../../composables/useCartNotification'
import type { Product } from '../../types/products'

vi.mock('vue-toastification', () => ({ useToast: () => ({}) }))
vi.mock('../../config/index', () => ({ productsApi: {} }))
const product = { id: 1, name: 'Campera', price: 100, is_unique: true, stock: 2, images: [] } as unknown as Product

describe('feedback al agregar al carrito', () => {
  beforeEach(() => { setActivePinia(createPinia()); localStorage.clear(); vi.useFakeTimers() })
  afterEach(() => { useCartNotification().hideNotification(); vi.useRealTimers() })
  it('agrega y anuncia los datos seleccionados', () => {
    const cart = useCartStore()
    expect(cart.addToCart(product, 1, undefined, { color: { id: 1, name: 'Negro' }, size: { id: 2, name: 'M' } })).toBe(true)
    expect(cart.itemCount).toBe(1)
    expect(useCartNotification().productData.value?.variant).toEqual({ color: 'Negro', size: 'M' })
  })
  it('rechaza sin stock sin cambiar el carrito', () => {
    const cart = useCartStore()
    expect(cart.addToCart({ ...product, stock: 0 }, 1)).toBe(false)
    expect(cart.itemCount).toBe(0)
    expect(useCartNotification().errorMessage.value).toContain('no tiene stock')
  })
  it('rechaza cantidades superiores al máximo y no anuncia un éxito', () => {
    const cart = useCartStore()
    expect(cart.addToCart(product, 3)).toBe(false)
    expect(cart.itemCount).toBe(0)
    expect(useCartNotification().errorMessage.value).toContain('máximo 2')
    expect(useCartNotification().productData.value).toBeNull()
  })
})
