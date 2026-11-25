import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PaymentSuccessView from '../PaymentSuccessView.vue'
import { orderAccessToken } from '../../../utils/orderAccess'

const mocks = vi.hoisted(() => ({ status: vi.fn(), clearCart: vi.fn() }))
vi.mock('vue-router', () => ({ useRoute: () => ({ query: { order_id: '9', access_token: 'private-order-token' } }) }))
vi.mock('../../../config/api', () => ({ paymentsApi: { getPaymentStatus: mocks.status } }))
vi.mock('../../../store/cart', () => ({ useCartStore: () => ({ clearCart: mocks.clearCart }) }))
afterEach(() => { vi.useRealTimers(); localStorage.clear(); vi.clearAllMocks() })

describe('Confirmación de pago invitado', () => {
  it('conserva el token y solo confirma al aprobar el servidor; consulta cada 5 segundos', async () => {
    vi.useFakeTimers()
    mocks.status.mockResolvedValueOnce({ payment_status: 'pending_payment' }).mockResolvedValue({ payment_status: 'approved', total: 2 })
    const wrapper = mount(PaymentSuccessView, { global: { stubs: { RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' } } } })
    await flushPromises()
    expect(orderAccessToken(9)).toBe('private-order-token')
    expect(orderAccessToken(10)).toBeUndefined()
    expect(wrapper.text()).toContain('Estamos confirmando tu pago')
    expect(mocks.clearCart).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(4999)
    expect(mocks.status).toHaveBeenCalledTimes(1)
    await vi.advanceTimersByTimeAsync(1)
    expect(wrapper.text()).toContain('Pago confirmado')
    expect(wrapper.get('a').attributes('href')).toContain('access_token=private-order-token')
    expect(mocks.clearCart).toHaveBeenCalledTimes(1)
    wrapper.unmount()
    await vi.advanceTimersByTimeAsync(10000)
    expect(mocks.status).toHaveBeenCalledTimes(2)
  })

  it('deja de consultar a los dos minutos sin inventar un pago aprobado', async () => {
    vi.useFakeTimers()
    mocks.status.mockResolvedValue({ payment_status: 'pending_payment' })
    const wrapper = mount(PaymentSuccessView, { global: { stubs: ['RouterLink'] } })
    await flushPromises()
    await vi.advanceTimersByTimeAsync(120000)
    expect(wrapper.text()).toContain('Pago pendiente')
    const count = mocks.status.mock.calls.length
    await vi.advanceTimersByTimeAsync(10000)
    expect(mocks.status).toHaveBeenCalledTimes(count)
    expect(mocks.clearCart).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
