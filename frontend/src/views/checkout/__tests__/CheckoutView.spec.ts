import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import CheckoutView from '../CheckoutView.vue'

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  createOrder: vi.fn(),
  cart: { isEmpty: false, items: [], totalPrice: 1000, totalSavings: 0, loadFromStorage: vi.fn(), validateStock: vi.fn() },
}))
vi.mock('../../../store/cart', () => ({ useCartStore: () => mocks.cart }))
vi.mock('../../../store/auth', () => ({ useAuthStore: () => ({ isAuthenticated: true, backendUser: null }) }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push: mocks.push, replace: mocks.push }) }))
vi.mock('vue-toastification', () => ({ useToast: () => ({ warning: vi.fn(), error: vi.fn() }) }))
vi.mock('../../../config/payments', () => ({ COMPRAS_HABILITADAS: true, MERCADOPAGO_HABILITADO: true }))
vi.mock('../../../config/api', () => ({ ordersApi: { createOrder: mocks.createOrder }, customersApi: {}, orderItemsApi: {}, paymentsApi: {} }))
vi.mock('../../../services/stockService', () => ({ stockService: {} }))
vi.mock('../../../composables/useUserData', () => ({ useUserData: () => ({ loadCustomerData: async () => null, getCheckoutFormData: vi.fn() }) }))

const scroll = vi.fn()
beforeEach(() => {
  vi.stubGlobal('matchMedia', () => ({ matches: false }))
  HTMLElement.prototype.scrollIntoView = scroll
  vi.clearAllMocks()
})
afterEach(() => { document.body.innerHTML = '' })

describe('Pasos del checkout con retiro único', () => {
  it('continúa del contacto al pago con foco, vuelve y conserva contacto y medio de pago', async () => {
    const wrapper = mount(CheckoutView, { attachTo: document.body, global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } } })
    await flushPromises()
    for (const [id, value] of Object.entries({ firstName: 'Ana', lastName: 'Pérez', email: 'ana@example.com', phone: '1123456789' })) {
      await wrapper.get(`#${id}`).setValue(value)
    }
    const next = wrapper.findAll('button').filter(button => button.text().includes('Continuar al pago'))
    expect(next).toHaveLength(1)
    await next[0].trigger('click')
    await flushPromises()
    expect(document.activeElement?.textContent).toBe('Método de pago')
    expect(scroll).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' })
    await wrapper.get('input[value="mercadopago"]').setValue()
    await wrapper.findAll('button').find(button => button.text().includes('Volver al contacto'))!.trigger('click')
    await flushPromises()
    expect(document.activeElement?.textContent).toBe('Información de contacto')
    expect((wrapper.get('#firstName').element as HTMLInputElement).value).toBe('Ana')
    await wrapper.findAll('button').find(button => button.text().includes('Continuar al pago'))!.trigger('click')
    await flushPromises()
    expect((wrapper.get('input[value="mercadopago"]').element as HTMLInputElement).checked).toBe(true)
    await wrapper.get('input[value="transfer"]').setValue()
    expect((wrapper.get('input[value="transfer"]').element as HTMLInputElement).checked).toBe(true)
    expect(mocks.createOrder).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
