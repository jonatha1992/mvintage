// @vitest-environment node
import { describe, it, expect, vi } from 'vitest'
import { generateSitemap, robotsText } from '../seo-build'

describe('sitemap de build', () => {
  it.each(['network', 'http', 'invalid', 'partial'])('tolera fallo %s con solo páginas estáticas', async kind => {
    const warning = vi.spyOn(console, 'warn').mockImplementation(() => {})
    try {
      const fetcher = vi.fn().mockImplementation(async () => {
        if (kind === 'network') throw new Error('Sin red')
        return new Response(JSON.stringify(kind === 'invalid' ? {} : [{ id: 2, name: 'Remera' }, { id: null }]), { status: kind === 'http' ? 503 : 200 })
      })
      const xml = await generateSitemap(fetcher)
      expect(xml).toContain('/contact</loc>')
      expect(xml).not.toContain('/product/')
      expect(warning).toHaveBeenCalledOnce()
    } finally { warning.mockRestore() }
  })
  it('separa robots test y producción', () => {
    expect(robotsText(true)).toContain('Disallow: /\n')
    expect(robotsText(true)).not.toContain('Allow: /')
    expect(robotsText(false)).toContain('Allow: /')
    expect(robotsText(false)).toContain('Disallow: /admin')
    expect(robotsText(false)).toContain('Sitemap: https://showroomisabella-ar.web.app/sitemap.xml')
  })
  it('incluye estáticas y productos con fecha y dominio canónico', async () => {
    const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify([{ id: 2, name: 'Remera Café & Rosa' }])))
    const xml = await generateSitemap(fetcher, new Date('2026-11-24T12:00:00Z'))
    expect(xml).toContain('https://showroomisabella-ar.web.app/product/2/remera-cafe-rosa')
    expect(xml).toContain('<lastmod>2026-11-24</lastmod>')
    expect(xml).toContain('https://showroomisabella-ar.web.app/contact')
    expect(xml).not.toContain('/cart')
    expect(xml).not.toContain('test.web.app')
  })
})
