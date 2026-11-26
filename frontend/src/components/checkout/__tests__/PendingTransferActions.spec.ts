import { afterEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import PendingTransferActions from '../PendingTransferActions.vue'

const api = vi.hoisted(() => ({ getOrder: vi.fn(), cancelPendingOrder: vi.fn(), payWithMercadoPago: vi.fn() }))
vi.mock('../../../config/api', () => ({ ordersApi: api }))
afterEach(() => { vi.restoreAllMocks(); vi.clearAllMocks() })

describe('Retractarse de transferencia', () => {
  it('pide confirmación y cancela solo si la clienta acepta', async () => {
    const pending = { payment_method: 'bank_transfer', payment_status: 'pending_payment' }
    api.getOrder.mockResolvedValue(pending)
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const wrapper = mount(PendingTransferActions, { props: { orderId: 9 } })
    await flushPromises()
    await wrapper.findAll('button')[1].trigger('click')
    expect(api.cancelPendingOrder).not.toHaveBeenCalled()
    confirm.mockReturnValue(true)
    api.getOrder.mockResolvedValue({ ...pending, payment_status: 'cancelled' })
    await wrapper.findAll('button')[1].trigger('click')
    await flushPromises()
    expect(api.cancelPendingOrder).toHaveBeenCalledWith(9)
    expect(wrapper.emitted('updated')).toHaveLength(1)
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('no ofrece cambiar ni cancelar una transferencia verificada', async () => {
    api.getOrder.mockResolvedValue({ payment_method: 'bank_transfer', payment_status: 'pending_payment', transfer_verified: true })
    const wrapper = mount(PendingTransferActions, { props: { orderId: 9 } })
    await flushPromises()
    expect(wrapper.find('button').exists()).toBe(false)
  })
})
