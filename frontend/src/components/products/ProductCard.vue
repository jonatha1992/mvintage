<template>
  <router-link v-reveal="index" :to="`/product/${product.id}/${product.name}`" class="block h-full">
    <div class="flex flex-col h-full overflow-hidden transition-shadow duration-200 bg-white border border-gray-300 rounded-lg shadow-sm hover:shadow-md group product-card">
      <!-- Imagen del producto -->
      <div
        class="relative overflow-hidden aspect-square bg-gray-50"
        @pointerenter="onPointerEnter"
      >
        <!-- Imagen principal -->
        <div class="absolute inset-0 pc-primary" :class="{ 'has-secondary': secondaryImage && shouldLoadHover }">
          <img
            :src="primaryImageSrc"
            :srcset="primaryImageSrcset"
            :sizes="CARD_IMAGE_SIZES"
            :alt="product.name"
            :loading="isFirstRow ? 'eager' : 'lazy'"
            :fetchpriority="isPriorityCard ? 'high' : undefined"
            :decoding="isFirstRow ? undefined : 'async'"
            width="400"
            height="400"
            class="object-cover w-full h-full"
            @error="handleImageError"
          />
        </div>

        <!-- Imagen secundaria (hover: solo en dispositivos con hover fino, cargada en pointerenter) -->
        <div v-if="secondaryImage && shouldLoadHover" class="absolute inset-0 opacity-0 pc-secondary">
          <img
            :src="secondaryImageSrc"
            :srcset="secondaryImageSrcset"
            :sizes="CARD_IMAGE_SIZES"
            :alt="product.name"
            loading="lazy"
            decoding="async"
            fetchpriority="low"
            width="400"
            height="400"
            class="object-cover w-full h-full"
            @error="handleImageError"
          />
        </div>

        <!-- Etiquetas de producto -->
        <div v-if="product.is_new || product.is_sale || hasActiveDiscount" class="absolute z-10 flex flex-col items-start gap-1 top-2 left-2">
          <span v-if="product.is_new" class="inline-block px-2 py-0.5 text-[10px] font-medium text-white bg-black uppercase">
            New
          </span>
          <span v-if="product.is_sale" class="inline-block px-2 py-0.5 text-[10px] font-medium text-white bg-red-600 uppercase">
            Sale
          </span>
          <span
            v-if="hasActiveDiscount && promoBadgeText"
            data-testid="promo-badge"
            class="inline-block px-2 py-0.5 text-[10px] font-semibold tracking-wide text-white bg-rose-700 uppercase promo-badge"
          >
            {{ promoBadgeText }}
          </span>
        </div>


        <!-- Etiqueta de SIN STOCK en esquina superior izquierda -->
        <div v-if="isOutOfStock" class="absolute top-0 left-0 z-10 mt-2 ml-4">
          <span class="px-3 py-1 text-xs font-bold text-white bg-gray-600 rounded-lg">SIN STOCK</span>
        </div>
      </div>

      <!-- Información del producto -->
      <div class="flex flex-col flex-1 p-3">
        <!-- Nombre del producto -->
        <h3 class="mb-1 text-sm font-normal leading-tight text-gray-800 line-clamp-2">
          {{ product.name }}
        </h3>

        <!-- Categoría -->
        <p v-if="product.categoria" class="mb-2 text-xs tracking-wider text-gray-500 uppercase">
          {{ product.categoria }}
        </p>
        
        <!-- Precios -->
        <div class="pt-2 mt-auto">
          <!-- Precio con descuento -->
          <div v-if="hasActiveDiscount" class="space-y-0.5">
            <span class="block text-sm font-bold text-rose-700" data-testid="discounted-price">
              {{ formatPrice(effectivePrice) }}
            </span>
            <span class="text-xs text-gray-400 line-through" data-testid="original-price">
              {{ formatPrice(product.price) }}
            </span>
          </div>
          
          <!-- Precio normal -->
          <div v-else>
            <span class="text-sm font-bold text-gray-900">
              {{ formatPrice(product.price) }}
            </span>
            <span v-if="product.original_price && product.original_price > product.price" 
                  class="ml-1.5 text-xs text-gray-400 line-through">
              {{ formatPrice(product.original_price) }}
            </span>
          </div>
          <p
            v-if="MERCADOPAGO_HABILITADO && cardInstallments > 1"
            data-testid="card-installments"
            class="mt-1 text-[11px] text-gray-600"
          >
            {{ cardInstallments }} x {{ formatPrice(Math.round(effectivePrice / cardInstallments)) }} sin interés
          </p>
        </div>
      </div>
    </div>
    
  </router-link>
</template>

<script setup lang="ts">
import { formatPrice, getEffectivePrice, getPromoBadgeText, isProductDiscountActive } from '../../utils/price'
import { MERCADOPAGO_HABILITADO } from '../../config/payments'
import { vReveal } from '../../composables/useReveal'
import { buildImageVariantUrl, buildImageSrcset } from '../../utils/imageUrl'
import { defineProps, computed, ref } from 'vue';
import type { Product } from '../../types/products/product.types';

const defaultImage = '/imagen-portada.svg';
const CARD_IMAGE_SIZES = '(max-width: 639px) 46vw, (max-width: 1023px) 45vw, (max-width: 1279px) 30vw, 23vw';

const props = defineProps<{
  product: Product;
  index?: number;
}>();

const primaryImageFailed = ref(false);
const shouldLoadHover = ref(false);

const isFirstRow = computed(() => (props.index ?? 0) < 4);
const isPriorityCard = computed(() => (props.index ?? 0) < 2);
const hasActiveDiscount = computed(() => isProductDiscountActive(props.product));
const effectivePrice = computed(() => getEffectivePrice(props.product));
const promoBadgeText = computed(() => getPromoBadgeText(props.product));
const cardInstallments = computed(() => props.product.max_installments ?? 1);

const canHover = (): boolean =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(hover: hover) and (pointer: fine)').matches;

const onPointerEnter = (event: PointerEvent) => {
  if (shouldLoadHover.value || event.pointerType === 'touch' || !canHover()) return;
  shouldLoadHover.value = true;
};

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  if (img.src !== defaultImage) {
    primaryImageFailed.value = true;
    img.srcset = '';
    img.src = defaultImage;
  }
};

const primaryImage = computed(() => {
  if (primaryImageFailed.value) {
    return defaultImage;
  }
  if (props.product.images && props.product.images[0] && props.product.images[0].image_url) {
    return props.product.images[0].image_url;
  }
  return defaultImage;
});

const primaryImageSrc = computed(() => buildImageVariantUrl(primaryImage.value, 800));
const primaryImageSrcset = computed(() => buildImageSrcset(primaryImage.value, [400, 800]));

const secondaryImage = computed(() => {
  if (props.product.images && props.product.images[1] && props.product.images[1].image_url) {
    return props.product.images[1].image_url;
  }
  return null;
});

const secondaryImageSrc = computed(() =>
  secondaryImage.value ? buildImageVariantUrl(secondaryImage.value, 800) : ''
);
const secondaryImageSrcset = computed(() =>
  secondaryImage.value ? buildImageSrcset(secondaryImage.value, [400, 800]) : undefined
);


// Determinar si el producto está sin stock
const isOutOfStock = computed(() => {
  // Para productos únicos (is_unique = true), verificar el stock directo
  if (props.product.is_unique) {
    return props.product.stock === 0 || props.product.stock === null;
  }
  
  // Para productos con variantes, verificar si todas las variantes tienen stock 0
  if (props.product.variants && props.product.variants.length > 0) {
    return props.product.variants.every((variant: any) => variant.stock === 0);
  }
  
  // Si no hay variantes y no es único, asumir que está disponible
  return false;
});

// Quick add function (placeholder)
const quickAdd = () => {
  // TODO: Implementar lógica de quick add
};
</script>

<style scoped>
/* Estilos para el contenedor de la tarjeta */
.router-link {
  display: block;
  height: 100%;
  text-decoration: none;
  color: inherit;
}

/* Estilos para la imagen */
.aspect-square {
  position: relative;
  width: 100%;
  padding-bottom: 100%; /* Mantener relaci  ón de aspecto 1:1 */
  overflow: hidden;
  background-color: #f9fafb;
}

/* Contenedor de imágenes */
.aspect-square > div {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Hover solo en dispositivos con puntero: zoom 1.04 y crossfade a la 2ª imagen */
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  img {
    transition: transform 280ms ease-out;
  }
  .group:hover img {
    transform: scale(1.04);
  }
}

@media (hover: hover) {
  .pc-primary,
  .pc-secondary {
    transition: opacity 250ms ease-out;
  }
  .group:hover .pc-primary.has-secondary {
    opacity: 0;
  }
  .group:hover .pc-secondary {
    opacity: 1;
  }
}

/* Estilos para las etiquetas de producto */
.bg-black, .bg-red-600, .bg-rose-700 {
  border-radius: 2px;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.05em;
  line-height: 1;
  padding: 0.25rem 0.45rem;
}

@media (prefers-reduced-motion: no-preference) {
  .promo-badge {
    animation: promoBadgePulse 3s ease-in-out infinite;
  }
}

@keyframes promoBadgePulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.03);
    opacity: 0.92;
  }
}

/* Estilos para el texto tachado */
.line-through {
  text-decoration-color: #9ca3af;
}

/* Mejoras de accesibilidad */
.router-link:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  transform: translateY(-1px);
}
</style>
