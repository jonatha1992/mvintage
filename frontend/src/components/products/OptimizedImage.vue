<template>
  <div class="relative" :class="containerClass">
    <!-- Spinner de carga -->
    <div 
      v-if="imageState.loading && showSpinner" 
      class="absolute inset-0 flex items-center justify-center bg-gray-100"
      :class="aspectRatioClass"
    >
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
    </div>
    <!-- Imagen -->
    <img
      ref="imageRef"
      :src="eagerLoad ? src : undefined"
      :data-src="eagerLoad ? undefined : src"
      :alt="alt"
      :loading="eagerLoad ? 'eager' : 'lazy'"
      :class="[
        imageClass,
        aspectRatioClass,
        'transition-opacity duration-300',
        imageState.loaded ? 'opacity-100' : 'opacity-0'
      ]"
      @load="handleLoad"
      @error="handleError"
    />
    <!-- Estado de error con fallback -->
    <div
      v-if="imageState.error && fallbackSrc"
      class="absolute inset-0 z-10"
    >
      <img
        :src="fallbackSrc"
        :alt="alt"
        :class="[imageClass, aspectRatioClass, 'opacity-100']"
        @load="handleFallbackLoad"
        @error="() => {}"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useImageLoading } from '../../composables/useImageLoading'
interface Props {
  src: string
  alt: string
  loading?: 'lazy' | 'eager'
  aspectRatio?: 'square' | 'video' | 'auto'
  showSpinner?: boolean
  fallbackSrc?: string
  imageClass?: string
  containerClass?: string
}
const props = withDefaults(defineProps<Props>(), {
  loading: 'lazy',
  aspectRatio: 'auto',
  showSpinner: true,
  imageClass: 'object-cover w-full h-full',
  containerClass: ''
})

// Define emits FIRST before using emit
const emit = defineEmits<{
  error: [src: string]
  load: [src: string]
}>()

const imageRef = ref<HTMLImageElement>()
const { getImageState, setImageLoading, setImageLoaded, setImageError, observeImage } = useImageLoading()
const eagerLoad = computed(() =>
  props.loading === 'eager' ||
  props.src.startsWith('blob:') ||
  props.src.includes('firebasestorage')
)
const imageState = computed(() => getImageState(props.src))

const aspectRatioClass = computed(() => {
  switch (props.aspectRatio) {
    case 'square': return 'aspect-square'
    case 'video': return 'aspect-video'
    default: return ''
  }
})
const handleLoad = () => {
  setImageLoaded(props.src)
  // Emit load event to parent
  emit('load', props.src)
}
const handleError = () => {
  setImageError(props.src)
  // Emit error event to parent
  emit('error', props.src)
}
const handleFallbackLoad = () => {
  setImageLoaded(props.src)
}
onMounted(() => {
  // Initialize loading state for all images
  setImageLoading(props.src, true)

  if (imageRef.value && !eagerLoad.value) {
    observeImage(imageRef.value)
  }
})
</script>

