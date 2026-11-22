import type { Directive } from 'vue'

const nativo = CSS.supports('(animation-timeline: view()) and (animation-range: entry)')
const sinReducir = matchMedia('(prefers-reduced-motion: no-preference)').matches

let observer: IntersectionObserver | null = null

const getObserver = (): IntersectionObserver => {
  observer ??= new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue
        entry.target.classList.add('is-visible')
        observer?.unobserve(entry.target)
      }
    },
    { rootMargin: '0px 0px -8% 0px' }
  )
  return observer
}

// Reveal con fade + translateY. Valor opcional: índice para el stagger (se repite cada 4 tarjetas).
export const vReveal: Directive<HTMLElement, number | undefined> = {
  mounted(el, { value }) {
    el.classList.add('reveal')
    el.style.setProperty('--reveal-i', String((value ?? 0) % 4))
    if (!nativo && sinReducir) getObserver().observe(el)
  },
  unmounted(el) {
    observer?.unobserve(el)
  }
}
