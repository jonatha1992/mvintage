import { PUBLIC_PAGES, PRIVATE_PATHS, SITE_URL, SITE_NAME, SITE_DESCRIPTION, SITE_IMAGE, productPath } from '../seo/site'
import type { Product } from '../types/products/product.types'

export interface SeoMeta {
  title: string
  description: string
  canonical: string
  image: string
  noindex: boolean
  product?: Record<string, unknown>
}

export function routeSeo(path: string, test: boolean): SeoMeta {
  const cleanPath = path.split(/[?#]/)[0] || '/'
  const canonicalPath = ({ '/retiro': '/shipping', '/guia-de-talles': '/size-guide' } as Record<string, string>)[cleanPath] ?? cleanPath
  const page = PUBLIC_PAGES[canonicalPath]
  const privatePath = PRIVATE_PATHS.find(prefix => cleanPath === prefix || cleanPath.startsWith(`${prefix}/`))
  const titles: Record<string, string> = { '/cart': 'Carrito', '/checkout': 'Finalizar compra', '/auth': 'Ingresar', '/profile': 'Mi perfil', '/orders': 'Mis pedidos', '/payment': 'Estado del pago', '/admin': 'Administración', '/verify-email': 'Verificar email', '/account': 'Mi cuenta' }
  const productRoute = /^\/product\/\d+(\/[^/]+)?\/?$/.test(cleanPath)
  return {
    title: `${page?.title ?? (privatePath ? titles[privatePath] : productRoute ? 'Prenda' : 'Página no encontrada')} | ${SITE_NAME}`,
    description: page?.description ?? SITE_DESCRIPTION,
    canonical: `${SITE_URL}${canonicalPath}`, image: SITE_IMAGE,
    noindex: test || !!privatePath || (!page && !productRoute),
  }
}

export function productSeo(product: Product, test: boolean): SeoMeta {
  const price = product.has_discount && product.discounted_price != null ? product.discounted_price : product.price
  const description = product.description?.trim() || `${product.name.trim()}. Consultá talles y disponibilidad en Showroom Isabella. Retiro en el local de González Catán, a coordinar por WhatsApp.`
  const canonical = `${SITE_URL}${productPath(product)}`
  const image = new URL(product.images[0]?.image_url || SITE_IMAGE, SITE_URL).href
  const inStock = product.is_unique ? (product.stock ?? 0) > 0 : product.variants.some(v => v.stock > 0)
  return {
    title: `${product.name.trim()} - ${new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 2 }).format(price)} | ${SITE_NAME}`,
    description, canonical, image, noindex: test,
    product: {
      '@context': 'https://schema.org', '@type': 'Product', name: product.name.trim(), description, image,
      offers: { '@type': 'Offer', price, priceCurrency: 'ARS', availability: `https://schema.org/${inStock ? 'InStock' : 'OutOfStock'}`, url: canonical },
    },
  }
}

export function applySeo(meta: SeoMeta): void {
  document.title = meta.title
  const entries: Array<[string, string, string]> = [
    ['name', 'description', meta.description], ['name', 'robots', meta.noindex ? 'noindex, nofollow' : 'index, follow'],
    ['property', 'og:title', meta.title], ['property', 'og:description', meta.description],
    ['property', 'og:url', meta.canonical], ['property', 'og:image', meta.image],
    ['name', 'twitter:title', meta.title], ['name', 'twitter:description', meta.description], ['name', 'twitter:image', meta.image],
  ]
  for (const [attribute, key, value] of entries) {
    let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)
    if (!element) {
      element = document.createElement('meta')
      element.setAttribute(attribute, key)
      document.head.append(element)
    }
    element.content = value
  }
  let canonical = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.rel = 'canonical'
    document.head.append(canonical)
  }
  canonical.href = meta.canonical
  document.getElementById('seo-product')?.remove()
  if (meta.product) {
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.id = 'seo-product'
    script.textContent = JSON.stringify(meta.product)
    document.head.append(script)
  }
}
