import { afterEach, describe, expect, it } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ImageGalleryModal from '../ImageGalleryModal.vue'

const images = [{ id: 1, image_url: '/one.jpg' }, { id: 2, image_url: '/two.jpg' }]
let wrapper: ReturnType<typeof mount>
afterEach(() => { wrapper?.unmount(); document.body.innerHTML = '' })

describe('Visor de fotos', () => {
  it('sale del ancestro transformado y abre un diálogo modal en body', async () => {
    const host = document.createElement('div')
    host.style.transform = 'translateY(0)'
    document.body.append(host)
    wrapper = mount(ImageGalleryModal, { attachTo: host, props: { isOpen: true, images } })
    await flushPromises()
    const dialog = document.body.querySelector('dialog')!
    expect(dialog).not.toBeNull()
    expect(dialog.parentElement).toBe(document.body)
    expect(dialog.open).toBe(true)
    expect(dialog.querySelector('button[aria-label="Cerrar visor"]')).not.toBeNull()
  })

  it('navega con flechas y swipe sin escuchar gestos fuera del visor', async () => {
    wrapper = mount(ImageGalleryModal, { props: { isOpen: true, images } })
    await flushPromises()
    const dialog = document.body.querySelector('dialog')!
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }))
    await flushPromises()
    expect(dialog.querySelector('img')!.getAttribute('src')).toContain('one')
    dialog.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }))
    await flushPromises()
    expect(dialog.querySelector('img')!.getAttribute('src')).toContain('two')
    dialog.dispatchEvent(new TouchEvent('touchstart', { touches: [{ clientX: 10, clientY: 20 } as Touch] }))
    dialog.dispatchEvent(new TouchEvent('touchend', { changedTouches: [{ clientX: 100, clientY: 25 } as Touch] }))
    await flushPromises()
    expect(dialog.querySelector('img')!.getAttribute('src')).toContain('one')
  })

  it('restaura el scroll al cerrar o desmontar', async () => {
    document.body.style.overflow = 'scroll'
    wrapper = mount(ImageGalleryModal, { props: { isOpen: true, images } })
    await flushPromises()
    expect(document.body.style.overflow).toBe('hidden')
    await wrapper.setProps({ isOpen: false })
    expect(document.body.style.overflow).toBe('scroll')
    await wrapper.setProps({ isOpen: true })
    wrapper.unmount()
    expect(document.body.style.overflow).toBe('scroll')
    document.body.style.overflow = ''
  })

  it('cierra por X, Escape y fondo, pero no al tocar la imagen', async () => {
    wrapper = mount(ImageGalleryModal, { props: { isOpen: true, images } })
    await flushPromises()
    const dialog = document.body.querySelector('dialog')!
    dialog.querySelector('img')!.click()
    expect(wrapper.emitted('close')).toBeUndefined()
    dialog.querySelector<HTMLButtonElement>('[aria-label="Cerrar visor"]')!.click()
    dialog.dispatchEvent(new Event('cancel', { cancelable: true }))
    dialog.click()
    expect(wrapper.emitted('close')).toHaveLength(3)
    await wrapper.setProps({ isOpen: false })
    expect(dialog.open).toBe(false)
  })
})
