import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import Navbar from '../Navbar.vue'

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('../../../store/auth', () => ({
  useAuthStore: () => ({ isAuthenticated: false, hasAdminAccess: false, firebaseUser: null, logout: vi.fn() })
}))
vi.mock('../../../store/cart', () => ({
  useCartStore: () => ({ itemCount: 2 })
}))
vi.mock('../../../composables/useCartModal', () => ({
  useCartModal: () => ({ openCartModal: vi.fn() })
}))
vi.mock('../../../composables/useCartNotification', () => ({
  useCartNotification: () => ({ additionId: ref(0) })
}))
vi.mock('../../../config/index', () => ({
  masterDataApi: { getCategoriesWithStock: async () => [], getCategories: async () => [] }
}))

const global = {
  stubs: {
    RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' }
  }
}

describe('Navbar móvil', () => {
  it('permite encoger la marca sin cortar ni achicar los botones móviles', () => {
    const wrapper = mount(Navbar, { global })
    const logoLink = wrapper.get('a[href="/"]')
    const logoContainer = logoLink.element.parentElement!
    const brandText = logoLink.get('span')
    const menuButton = wrapper.get('button[aria-controls="mobile-menu"]')
    const mobileActions = menuButton.element.parentElement!
    const mobileButtons = Array.from(mobileActions.querySelectorAll('button'))

    expect(logoContainer.className).toContain('min-w-0')
    expect(brandText.classes()).toContain('truncate')
    expect(mobileActions.className).toContain('flex-shrink-0')
    expect(mobileButtons).toHaveLength(3)
    for (const btn of mobileButtons) {
      expect(btn.className).toContain('flex-shrink-0')
      expect(btn.className).toContain('min-w-11')
      expect(btn.className).toContain('min-h-11')
    }
  })

  it('incluye el botón de búsqueda en desktop y mobile y abre el dialog nativo', async () => {
    const wrapper = mount(Navbar, { global })
    const searchButtons = wrapper.findAll('button[aria-label="Buscar prendas"]')
    expect(searchButtons).toHaveLength(2)
    const dialog = wrapper.get('dialog').element as HTMLDialogElement
    expect(dialog.open).toBe(false)
    await searchButtons[0].trigger('click')
    expect(dialog.open).toBe(true)
  })
})
