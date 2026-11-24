export const SITE_URL = 'https://showroomisabella-ar.web.app'
export const SITE_NAME = 'Showroom Isabella'
export const SITE_DESCRIPTION = 'Ropa de mujer en González Catán. Descubrí la colección de Showroom Isabella y coordiná tu retiro en Alonso Pareja 6542 por WhatsApp.'
export const SITE_IMAGE = `${SITE_URL}/logo_redondo.jpg`

export const PUBLIC_PAGES: Record<string, { title: string; description: string }> = {
  '/': { title: 'Ropa de mujer en González Catán', description: SITE_DESCRIPTION },
  '/shop': { title: 'Colección de ropa de mujer', description: 'Explorá remeras, tops, blusas, conjuntos y más en Showroom Isabella. Consultá talles y stock y retirá tu compra en González Catán.' },
  '/contact': { title: 'Contacto', description: 'Visitá Showroom Isabella en Alonso Pareja 6542, González Catán. Coordiná horarios y retiro por WhatsApp al +54 9 11 7637-2876.' },
  '/how-to-shop': { title: 'Cómo comprar', description: 'Elegí tus prendas, consultá disponibilidad y coordiná el retiro de tu compra en Showroom Isabella por WhatsApp. Solo retiro en el local.' },
  '/shipping': { title: 'Retiro en el local', description: 'Retirá tu compra sin costo en Alonso Pareja 6542, González Catán. Los horarios se coordinan por WhatsApp. No realizamos envíos.' },
  '/size-guide': { title: 'Guía de talles', description: 'Consultá la guía de talles de Showroom Isabella para elegir tus prendas. Escribinos por WhatsApp si necesitás ayuda antes de comprar.' },
  '/terms': { title: 'Términos y condiciones', description: 'Conocé las condiciones de compra, retiro y cambios de Showroom Isabella, tienda de ropa de mujer en González Catán.' },
  '/privacy': { title: 'Política de privacidad', description: 'Conocé cómo Showroom Isabella utiliza y protege tus datos personales al navegar, crear una cuenta o realizar una compra.' },
}
export const PRIVATE_PATHS = ['/admin', '/checkout', '/cart', '/account', '/auth', '/verify-email', '/orders', '/profile', '/payment']

export function productPath(product: { id: number; name: string }): string {
  const slug = product.name.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  return `/product/${product.id}/${slug || 'prenda'}`
}

export const STORE_SCHEMA = {
  '@context': 'https://schema.org', '@type': 'ClothingStore',
  '@id': `${SITE_URL}/#store`, name: SITE_NAME, url: `${SITE_URL}/`,
  description: SITE_DESCRIPTION, logo: SITE_IMAGE, image: SITE_IMAGE,
  telephone: '+5491176372876', email: 'Showroomisabella@gmail.com',
  address: { '@type': 'PostalAddress', streetAddress: 'Alonso Pareja 6542', addressLocality: 'González Catán', addressRegion: 'Buenos Aires', addressCountry: 'AR' },
  sameAs: ['https://www.instagram.com/showroomisabella_/'],
}
