import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContactView from '../ContactView.vue'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('../../../config/index', () => ({ apiClient: { post } }))

describe('Contacto', () => {
  it('envía por POST, evita duplicados y confirma sin cambiar la URL', async () => {
    let resolve!: (value: unknown) => void
    post.mockReturnValueOnce(new Promise(done => { resolve = done }))
    const wrapper = mount(ContactView)
    await wrapper.get('#name').setValue('Ana')
    await wrapper.get('#email').setValue('ana@example.com')
    await wrapper.get('#message').setValue('Quiero consultar por una remera.')
    await wrapper.get('form').trigger('submit')
    await wrapper.get('form').trigger('submit')
    expect(post).toHaveBeenCalledTimes(1)
    expect(post).toHaveBeenCalledWith('/contact', {
      nombre: 'Ana', email: 'ana@example.com', mensaje: 'Quiero consultar por una remera.'
    })
    expect(wrapper.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    resolve({ data: {} })
    await flushPromises()
    expect(wrapper.get('[role="status"]').text()).toContain('Recibimos tu mensaje')
    expect(wrapper.get<HTMLTextAreaElement>('#message').element.value).toBe('')
  })

  it('conserva el mensaje y ofrece WhatsApp si falla', async () => {
    post.mockRejectedValueOnce(new Error('network'))
    const wrapper = mount(ContactView)
    await wrapper.get('#message').setValue('Una consulta para conservar')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('No pudimos enviar')
    expect(wrapper.get<HTMLTextAreaElement>('#message').element.value).toBe('Una consulta para conservar')
    expect(wrapper.get('a[href^="https://wa.me/"]').text()).toContain('WhatsApp')
  })
})
