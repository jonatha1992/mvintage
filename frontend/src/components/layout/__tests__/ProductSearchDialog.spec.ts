import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ProductSearchDialog from '../ProductSearchDialog.vue'
import { SEARCH_DEBOUNCE_MS, SEARCH_RESULT_LIMIT } from '../../../composables/useProductSearch'

const { push, getProducts } = vi.hoisted(() => ({
  push: vi.fn(),
  getProducts: vi.fn(),
}))

vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('../../../config/index', () => ({
  productsApi: { getProducts },
}))

const sampleProducts = [
  {
    id: 11,
    name: 'Blusa Vela',
    description: 'Lino liviano',
    price: 33000,
    categoria: 'BLUSA',
    is_unique: false,
    has_discount: true,
    discount_percentage: 20,
    discount_active: true,
    discounted_price: 26400,
    images: [{ id: 1, image_url: 'https://res.cloudinary.com/demo/image/upload/blusa.jpg' }],
    variants: [{ id: 1, color: 'Bordo', talle: 'M', stock: 3 }],
  },
  {
    id: 12,
    name: 'Pantalón Recto',
    description: 'Denim',
    price: 45000,
    categoria: 'PANTALON',
    is_unique: true,
    color: 'Negro',
    stock: 0,
    has_discount: false,
    images: [],
    variants: [],
  },
]

describe('ProductSearchDialog', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    push.mockReset()
    getProducts.mockReset()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('usa dialog nativo accesible sin atributos prohibidos', () => {
    const wrapper = mount(ProductSearchDialog)
    const dialog = wrapper.get('dialog')
    expect(dialog.attributes('closedby')).toBe('any')
    expect(dialog.attributes('role')).toBeUndefined()
    expect(dialog.attributes('aria-modal')).toBeUndefined()
    expect(dialog.attributes('aria-labelledby')).toBe('product-search-title')
    expect(wrapper.get('input[type="search"]').attributes('autofocus')).toBeDefined()
    expect(wrapper.find('button[type="button"][aria-label="Cerrar buscador"]').exists()).toBe(true)
  })

  it('busca con debounce y limit=8, muestra descuento y sin stock, y navega al producto', async () => {
    getProducts.mockResolvedValue({ products: sampleProducts, total: 2 })
    const wrapper = mount(ProductSearchDialog)
    ;(wrapper.vm as { open: () => void }).open()

    const input = wrapper.get('input[type="search"]')
    await input.setValue('blusa')
    expect(getProducts).not.toHaveBeenCalled()

    vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS)
    await flushPromises()

    expect(getProducts).toHaveBeenCalledTimes(1)
    expect(getProducts).toHaveBeenCalledWith(
      { search: 'blusa', limit: SEARCH_RESULT_LIMIT },
      expect.objectContaining({ signal: expect.any(AbortSignal) })
    )
    expect(wrapper.text()).toContain('Blusa Vela')
    expect(wrapper.text()).toContain('$26.400')
    expect(wrapper.text()).toContain('$33.000')
    expect(wrapper.text()).toContain('-20%')
    expect(wrapper.text()).toContain('Pantalón')
    expect(wrapper.text()).toContain('Sin stock')

    const resultButtons = wrapper.findAll('ul button')
    await resultButtons[0].trigger('click')
    expect(push).toHaveBeenCalledWith('/product/11')
    expect((wrapper.get('dialog').element as HTMLDialogElement).open).toBe(false)
  })

  it('cancela búsquedas anteriores con AbortController al escribir rápido', async () => {
    const signals: AbortSignal[] = []
    getProducts.mockImplementation((_params, opts?: { signal?: AbortSignal }) => {
      if (opts?.signal) signals.push(opts.signal)
      return new Promise(() => {})
    })

    const wrapper = mount(ProductSearchDialog)
    const input = wrapper.get('input[type="search"]')
    await input.setValue('blu')
    vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS)
    await flushPromises()
    expect(signals).toHaveLength(1)
    expect(signals[0].aborted).toBe(false)

    await input.setValue('blusa')
    expect(signals[0].aborted).toBe(true)
  })

  it('respeta composición IME en Enter y navega a /shop?q= en Enter normal', async () => {
    getProducts.mockResolvedValue({ products: [], total: 0 })
    const wrapper = mount(ProductSearchDialog)
    ;(wrapper.vm as { open: () => void }).open()
    const input = wrapper.get('input[type="search"]')
    await input.setValue('remera')

    await input.trigger('keydown', { key: 'Enter', isComposing: true })
    expect(push).not.toHaveBeenCalled()

    await input.trigger('keydown', { key: 'Enter', keyCode: 229 })
    expect(push).not.toHaveBeenCalled()

    await input.trigger('keydown', { key: 'Enter' })
    expect(push).toHaveBeenCalledWith({ path: '/shop', query: { q: 'remera' } })
    expect((wrapper.get('dialog').element as HTMLDialogElement).open).toBe(false)
  })

  it('cierra por fallback pointerdown+pointerup fuera del rect cuando closedBy no existe', async () => {
    const wrapper = mount(ProductSearchDialog)
    const dialogEl = wrapper.get('dialog').element as HTMLDialogElement
    ;(wrapper.vm as { open: () => void }).open()
    expect(dialogEl.open).toBe(true)

    vi.spyOn(dialogEl, 'getBoundingClientRect').mockReturnValue({
      left: 100,
      right: 500,
      top: 100,
      bottom: 400,
      width: 400,
      height: 300,
      x: 100,
      y: 100,
      toJSON: () => ({}),
    })

    // Down inside, up outside -> must NOT close
    await wrapper.get('dialog').trigger('pointerdown', { clientX: 200, clientY: 200 })
    await wrapper.get('dialog').trigger('pointerup', { clientX: 20, clientY: 20 })
    expect(dialogEl.open).toBe(true)

    // Down outside, up outside -> closes
    await wrapper.get('dialog').trigger('pointerdown', { clientX: 20, clientY: 20 })
    await wrapper.get('dialog').trigger('pointerup', { clientX: 25, clientY: 25 })
    expect(dialogEl.open).toBe(false)
  })
})
