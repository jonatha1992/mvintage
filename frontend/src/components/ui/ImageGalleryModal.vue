<template>
  <Teleport to="body">
    <dialog ref="dialog" class="image-gallery" aria-label="Fotos del producto" closedby="any"
      @cancel.prevent="closeModal" @click.self="closeModal" @keydown="handleKeydown"
      @touchstart="handleTouchStart" @touchend="handleTouchEnd">
      <button type="button" autofocus class="gallery-control gallery-close" aria-label="Cerrar visor" @click="closeModal">×</button>
      <img :src="currentImageSrc" :srcset="currentImageSrcset" sizes="100vw" :alt="alt"
        decoding="async" class="gallery-image" />
      <template v-if="images.length > 1">
        <button type="button" class="gallery-control gallery-previous" aria-label="Foto anterior"
          :disabled="currentIndex === 0" @click="previousImage">‹</button>
        <button type="button" class="gallery-control gallery-next" aria-label="Foto siguiente"
          :disabled="currentIndex === images.length - 1" @click="nextImage">›</button>
        <p class="gallery-counter" aria-live="polite">{{ currentIndex + 1 }} / {{ images.length }}</p>
      </template>
    </dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue';
import type { ProductImage } from '../../types/products/product.types';
import { buildImageVariantUrl, buildImageSrcset } from '../../utils/imageUrl';

const props = withDefaults(defineProps<{
  isOpen: boolean;
  images: ProductImage[];
  initialIndex?: number;
  alt?: string;
}>(), { initialIndex: 0, alt: 'Imagen del producto' });
const emit = defineEmits<{ (e: 'close'): void }>();
const dialog = ref<HTMLDialogElement | null>(null);
const currentIndex = ref(0);
const currentImage = computed(() => props.images[currentIndex.value]?.image_url ?? '');
const currentImageSrc = computed(() => buildImageVariantUrl(currentImage.value, 800));
const currentImageSrcset = computed(() => buildImageSrcset(currentImage.value, [400, 800]));
const closeModal = () => emit('close');
const previousImage = () => { if (currentIndex.value > 0) currentIndex.value--; };
const nextImage = () => { if (currentIndex.value < props.images.length - 1) currentIndex.value++; };
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft') { event.preventDefault(); previousImage(); }
  if (event.key === 'ArrowRight') { event.preventDefault(); nextImage(); }
};
let startX = 0;
let startY = 0;
const handleTouchStart = (event: TouchEvent) => {
  startX = event.touches[0].clientX;
  startY = event.touches[0].clientY;
};
const handleTouchEnd = (event: TouchEvent) => {
  const deltaX = event.changedTouches[0].clientX - startX;
  const deltaY = event.changedTouches[0].clientY - startY;
  if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
    if (deltaX > 0) previousImage();
    else nextImage();
  }
};
let previousOverflow: string | undefined;
watch([() => props.isOpen, dialog], ([open, element]) => {
  if (!element) return;
  if (open) {
    currentIndex.value = props.initialIndex;
    if (!element.open) {
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      element.showModal();
    }
  } else if (element.open) {
    element.close();
    document.body.style.overflow = previousOverflow ?? '';
    previousOverflow = undefined;
  }
}, { flush: 'post' });
watch(() => props.initialIndex, index => { if (props.isOpen) currentIndex.value = index; });
onBeforeUnmount(() => {
  dialog.value?.close();
  if (previousOverflow !== undefined) document.body.style.overflow = previousOverflow;
});
</script>

<style scoped>
.image-gallery {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100dvh;
  max-width: none;
  max-height: none;
  margin: 0;
  padding: 0;
  border: 0;
  color: white;
  background: rgb(0 0 0 / 90%);
  overflow: hidden;
  overscroll-behavior: contain;
}
.image-gallery[open] { display: flex; align-items: center; justify-content: center; }
.image-gallery::backdrop { background: transparent; overflow: hidden; overscroll-behavior: contain; }
.gallery-image { object-fit: contain; max-width: 100%; max-height: 90dvh; }
.gallery-control {
  position: absolute;
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgb(0 0 0 / 60%);
  color: white;
  font-size: 32px;
  transition: background-color 150ms ease-out;
}
.gallery-control:disabled { opacity: .3; }
.gallery-control:focus-visible { outline: 2px solid white; outline-offset: 2px; }
.gallery-close { top: 16px; right: 16px; }
.gallery-previous { left: 16px; }
.gallery-next { right: 16px; }
.gallery-counter { position: absolute; bottom: 8px; left: 0; right: 0; text-align: center; }
@media (prefers-reduced-motion: no-preference) {
  .image-gallery[open] { animation: gallery-fade 180ms ease-out; }
  @keyframes gallery-fade { from { opacity: 0; } to { opacity: 1; } }
}
</style>
