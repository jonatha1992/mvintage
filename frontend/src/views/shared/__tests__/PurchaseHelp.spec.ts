import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import HowToShopView from '../HowToShopView.vue'
import ShippingView from '../ShippingView.vue'

const flags = vi.hoisted(() => ({ COMPRAS_HABILITADAS: false, MERCADOPAGO_HABILITADO: false, WHATSAPP_NUMBER: '5491176372876' }))
vi.mock('../../../config/payments', () => flags)
const global = { stubs: { RouterLink: { template: '<a><slot /></a>' } } }

for (const purchases of [false, true]) {
  for (const mercadoPago of [false, true]) {
    describe(`Ayuda compras=${purchases} MercadoPago=${mercadoPago}`, () => {
      it('solo promete los medios habilitados', () => {
        flags.COMPRAS_HABILITADAS = purchases
        flags.MERCADOPAGO_HABILITADO = mercadoPago
        for (const component of [HowToShopView, ShippingView]) {
          const wrapper = mount(component, { global })
          expect(wrapper.text().includes('Mercado Pago')).toBe(purchases && mercadoPago)
          if (!purchases) expect(wrapper.text()).toContain('WhatsApp')
          expect(wrapper.text()).not.toContain('checkout')
          expect(wrapper.text()).not.toContain('JACKET')
        }
      })
    })
  }
}
