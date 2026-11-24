import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import ProductDetail from '../ProductDetail.vue'
import CollectionView from '../../../views/products/CollectionView.vue'
import ShoppingCart from '../../cart/ShoppingCart.vue'

const { product, push } = vi.hoisted(() => ({
  product: { id: 11, name: 'Blusa VELA', price: 33000, images: [], is_unique: false,
    variants: [{ id: 1, color: 'BEIGE', talle: 'M', stock: 5 }] },
  push: vi.fn()
}))
vi.mock('vue-router', () => ({ useRoute: () => ({ params: { id: '11' }, query: {} }), useRouter: () => ({ push }) }))
vi.mock('../../../config/index', () => ({
  productsApi: { getProducts: async () => ({ products: [product] }) },
  masterDataApi: { getColors: async () => [], getSizes: async () => [], getCategoriesWithStock: async () => [{ id: 1, name: 'BLUSA' }] }
}))
vi.mock('../../../store/products', () => ({ useProducts: () => ({ products: ref([product]), isLoading: ref(false), ensureProducts: vi.fn() }) }))
vi.mock('../../../store/cart', () => ({ useCartStore: () => ({
  items: [{ id: '11', product, quantity: 1 }], isEmpty: false, itemCount: 1,
  getItemTotal: () => 33000, totalPrice: 33000, validateStock: vi.fn()
}) }))
vi.mock('../../../store/auth', () => ({ useAuthStore: () => ({ isAuthenticated: false }) }))
vi.mock('vue-toastification', () => ({ useToast: () => ({ warning: vi.fn(), error: vi.fn() }) }))
const global = { stubs: { RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' }, ImageGalleryModal: true } }

describe('Regresiones QA', () => {
  it('el carrito enlaza al identificador del producto', () => {
    const wrapper = mount(ShoppingCart, { global })
    expect(wrapper.get('h3 a').attributes('href')).toMatch(/^\/product\/11(?:\/|$)/)
  })
  it('la cantidad ingresada se ajusta al stock de la variante', async () => {
    const wrapper = mount(ProductDetail, { global })
    await flushPromises()
    const input = wrapper.get<HTMLInputElement>('input[aria-label="Cantidad"]')
    await input.setValue('99')
    await input.trigger('blur')
    expect(Number(input.element.value)).toBe(5)
    await input.setValue('1.5')
    await input.trigger('blur')
    expect(Number(input.element.value)).toBe(1)
  })
  it('el panel móvil ofrece precio, orden y limpieza', async () => {
    const wrapper = mount(CollectionView, { global })
    await flushPromises()
    expect(wrapper.find('dialog').exists()).toBe(true)
    expect(wrapper.get('dialog').text()).toContain('Precio')
    expect(wrapper.get('dialog').text()).toContain('Ordenar por')
    expect(wrapper.get('dialog').text()).toContain('Limpiar filtros')
  })
})
