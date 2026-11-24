import { describe, it, expect, beforeEach } from 'vitest'
import { routeSeo, productSeo, applySeo } from '../seo'
import type { Product } from '../../types/products/product.types'

describe('metadatos de navegación', () => {
  beforeEach(() => { document.head.innerHTML = '' })
  const product: Product = { id: 2, name: 'Remera Café', description: 'Remera de algodón.', price: 14000, has_discount: false, is_unique: false, images: [{ id: 1, image_url: 'https://img.tecnofusion.dev/remera.webp' }], variants: [{ stock: 1 }] }
  it.each(['/admin/products', '/checkout', '/cart', '/account', '/auth', '/profile', '/orders/2', '/payment/success', '/ruta-inexistente'])('no indexa %s', path => {
    expect(routeSeo(path, false).noindex).toBe(true)
  })
  it('mantiene producción indexable y test bloqueado', () => {
    expect(routeSeo('/shop', false).noindex).toBe(false)
    expect(routeSeo('/shop', true).noindex).toBe(true)
    expect(routeSeo('/retiro', false).canonical).toMatch(/\/shipping$/)
  })
  it('usa precio, descripción, imagen y stock reales y limpia Product al salir', () => {
    const meta = productSeo(product, false)
    applySeo(meta)
    expect(document.title).toContain('Remera Café - $')
    expect(document.title).toContain('14.000')
    expect(document.querySelector('meta[property="og:image"]')?.getAttribute('content')).toBe(product.images[0]?.image_url)
    expect(meta.product?.offers).toMatchObject({ price: 14000, priceCurrency: 'ARS', availability: 'https://schema.org/InStock', url: 'https://showroomisabella-ar.web.app/product/2/remera-cafe' })
    expect(document.querySelector('meta[name="description"]')?.getAttribute('content')).toBe(product.description)
    applySeo(routeSeo('/shop', false))
    expect(document.getElementById('seo-product')).toBeNull()
    expect(document.querySelectorAll('link[rel="canonical"]')).toHaveLength(1)
  })
  it('usa descuento y distingue stock único y variantes agotadas', () => {
    expect(productSeo({ ...product, has_discount: true, discounted_price: 10000 }, true).product?.offers).toMatchObject({ price: 10000 })
    expect(productSeo({ ...product, variants: [{ stock: 0 }] }, false).product?.offers).toMatchObject({ availability: 'https://schema.org/OutOfStock' })
    expect(productSeo({ ...product, is_unique: true, stock: 0 }, false).product?.offers).toMatchObject({ availability: 'https://schema.org/OutOfStock' })
    expect(productSeo({ ...product, is_unique: true, stock: 2 }, true).noindex).toBe(true)
  })
  it('inserta los datos como texto sin interpretar HTML', () => {
    applySeo(productSeo({ ...product, name: '<img src=x onerror=alert(1)>', description: '</script><script>alert(1)</script>', images: [] }, false))
    expect(document.head.querySelector('img')).toBeNull()
    expect(JSON.parse(document.getElementById('seo-product')!.textContent!).description).toBe('</script><script>alert(1)</script>')
    expect(document.querySelector('meta[property="og:image"]')?.getAttribute('content')).toBe('https://showroomisabella-ar.web.app/logo_redondo.jpg')
  })
  it('actualiza canonical, título y descripción sin query ni hash', () => {
    applySeo(routeSeo('/contact?from=home#local', false))
    expect(document.title).toBe('Contacto | Showroom Isabella')
    expect(document.querySelector('link[rel="canonical"]')?.getAttribute('href')).toBe('https://showroomisabella-ar.web.app/contact')
    expect(document.querySelector('meta[name="description"]')?.getAttribute('content')).toContain('Alonso Pareja 6542')
  })
})
