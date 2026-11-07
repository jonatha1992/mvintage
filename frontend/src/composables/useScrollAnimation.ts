import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface ScrollAnimationOptions {
  threshold?: number
  rootMargin?: string
  once?: boolean
  delay?: number
}

interface AnimationElement {
  element: HTMLElement
  options: ScrollAnimationOptions
  hasTriggered: boolean
}

export function useScrollAnimation() {
  const observer = ref<IntersectionObserver | null>(null)
  const elements = ref<AnimationElement[]>([])

  const createObserver = () => {
    if (typeof window === 'undefined') return

    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const elementData = elements.value.find(el => el.element === entry.target)
          if (!elementData) return

          if (entry.isIntersecting) {
            // Element is visible, add animation class
            const { delay = 0 } = elementData.options

            setTimeout(() => {
              entry.target.classList.add('animate-in')
              entry.target.classList.remove('animate-out')
            }, delay)

            // Mark as triggered if once=true
            if (elementData.options.once) {
              elementData.hasTriggered = true
              observer.value?.unobserve(entry.target)
            }
          } else {
            // Element is not visible
            if (!elementData.options.once || !elementData.hasTriggered) {
              entry.target.classList.remove('animate-in')
              entry.target.classList.add('animate-out')
            }
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
    )
  }

  const addElement = (
    element: HTMLElement | null,
    options: ScrollAnimationOptions = {}
  ) => {
    if (!element || !observer.value) return

    const defaultOptions: ScrollAnimationOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px',
      once: true,
      delay: 0,
      ...options
    }

    // Add initial classes
    element.classList.add('scroll-animated')
    element.classList.add('animate-out')

    const elementData: AnimationElement = {
      element,
      options: defaultOptions,
      hasTriggered: false
    }

    elements.value.push(elementData)
    observer.value.observe(element)
  }

  const addElements = (
    selector: string,
    options: ScrollAnimationOptions = {}
  ) => {
    nextTick(() => {
      const nodeList = document.querySelectorAll(selector)
      nodeList.forEach((element, index) => {
        if (element instanceof HTMLElement) {
          addElement(element, {
            ...options,
            delay: (options.delay || 0) + (index * 100) // Stagger animation
          })
        }
      })
    })
  }

  const removeElement = (element: HTMLElement) => {
    if (!observer.value) return

    observer.value.unobserve(element)
    elements.value = elements.value.filter(el => el.element !== element)
  }

  const cleanup = () => {
    if (observer.value) {
      observer.value.disconnect()
      observer.value = null
    }
    elements.value = []
  }

  onMounted(() => {
    createObserver()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    addElement,
    addElements,
    removeElement,
    cleanup
  }
}

// Predefined animation sets for common use cases
export const animationPresets = {
  fadeInUp: 'fade-in-up',
  fadeInDown: 'fade-in-down',
  fadeInLeft: 'fade-in-left',
  fadeInRight: 'fade-in-right',
  scaleIn: 'scale-in',
  slideInUp: 'slide-in-up',
  slideInDown: 'slide-in-down'
}