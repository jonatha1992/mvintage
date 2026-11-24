import type { Plugin } from 'vite'
import { readFile, writeFile } from 'node:fs/promises'
import { execFileSync } from 'node:child_process'
import { resolve } from 'node:path'
import { PRIVATE_PATHS, PUBLIC_PAGES, SITE_URL, STORE_SCHEMA } from '../src/seo/site'
import { productPath } from '../src/seo/site'

export function robotsText(test: boolean): string {
  return `User-agent: *\n${test ? 'Disallow: /' : `Allow: /\n${PRIVATE_PATHS.map(path => `Disallow: ${path}`).join('\n')}`}\n\nSitemap: ${SITE_URL}/sitemap.xml\n`
}

export async function generateSitemap(fetcher: typeof fetch = fetch, now = new Date()): Promise<string> {
  const paths = new Set(Object.keys(PUBLIC_PAGES))
  try {
    const response = await fetcher('https://showroomisabella-api.tecnofusion.dev/api/v1/products/', { signal: AbortSignal.timeout(15000) })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const products: unknown = await response.json()
    if (!Array.isArray(products)) throw new Error('Respuesta de catálogo inválida')
    for (const product of products) {
      if (!Number.isInteger(product.id) || product.id <= 0 || typeof product.name !== 'string') throw new Error('Producto inválido en catálogo')
      paths.add(productPath(product))
    }
  } catch (error) {
    console.warn('[SEO] No se pudo leer el catálogo; sitemap con rutas estáticas.', error)
    for (const path of paths) if (path.startsWith('/product/')) paths.delete(path)
  }
  const lastmod = now.toISOString().slice(0, 10)
  const urls = [...paths].map(path => `  <url><loc>${SITE_URL}${path}</loc><lastmod>${lastmod}</lastmod></url>`)
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`
}

export function seoBuild(mode: string): Plugin {
  let outDir: string
  let root: string
  return {
    name: 'showroom-seo',
    configResolved(config) { root = config.root; outDir = resolve(root, config.build.outDir) },
    transformIndexHtml(html) {
      return html.replace('%SEO_ROBOTS%', mode === 'pro' || mode === 'production' ? 'index, follow' : 'noindex, nofollow').replace('%SEO_STORE%', JSON.stringify(STORE_SCHEMA).replace(/</g, '\\u003c'))
    },
    async closeBundle() {
      const version = (await readFile(resolve(root, '../VERSION'), 'utf8')).trim()
      const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim()
      await Promise.all([
        writeFile(resolve(outDir, 'version.json'), JSON.stringify({ version, commit, builtAt: new Date().toISOString() }) + '\n'),
        writeFile(resolve(outDir, 'robots.txt'), robotsText(mode !== 'pro' && mode !== 'production')),
        generateSitemap().then(xml => writeFile(resolve(outDir, 'sitemap.xml'), xml)),
      ])
    },
  }
}
