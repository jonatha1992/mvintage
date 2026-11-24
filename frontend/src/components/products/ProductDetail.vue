<template>
  <div class="min-h-screen bg-white">
    <nav class="px-4 py-4 mx-auto max-w-6xl lg:px-8" aria-label="Ubicación">
      <ol class="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-gray-500 sm:text-sm">
        <li><router-link to="/" class="hover:text-gray-900">Inicio</router-link></li>
        <li aria-hidden="true">/</li>
        <li><router-link to="/shop" class="hover:text-gray-900">Colección</router-link></li>
        <template v-if="product">
          <template v-if="product.categoria">
            <li aria-hidden="true">/</li>
            <li>{{ product.categoria }}</li>
          </template>
          <li aria-hidden="true">/</li>
          <li class="font-medium text-gray-900" aria-current="page">{{ product.name }}</li>
        </template>
      </ol>
    </nav>

    <div v-if="!product && loading" class="mx-auto max-w-6xl lg:px-8 lg:grid lg:grid-cols-2 lg:gap-x-12" aria-hidden="true">
      <div class="skeleton aspect-[4/5] lg:rounded-lg"></div>
      <div class="px-4 mt-6 space-y-4 lg:mt-0 lg:px-0">
        <div class="w-3/4 h-7 rounded skeleton"></div>
        <div class="w-1/3 h-6 rounded skeleton"></div>
        <div class="flex gap-2 pt-4">
          <div class="w-20 h-10 rounded-md skeleton"></div>
          <div class="w-20 h-10 rounded-md skeleton"></div>
          <div class="w-20 h-10 rounded-md skeleton"></div>
        </div>
        <div class="h-14 rounded-md skeleton"></div>
      </div>
    </div>

    <div v-if="product" class="mx-auto max-w-6xl lg:px-8 lg:grid lg:grid-cols-2 lg:gap-x-12">
      <!-- Galería -->
      <section aria-label="Galería de imágenes" class="lg:flex lg:flex-row-reverse lg:gap-4 lg:items-start">
        <div class="relative flex-1 min-w-0">
          <div
            ref="galleryTrack"
            class="gallery-track product-main-image bg-gray-100 lg:rounded-lg"
            tabindex="0"
            @scroll.passive="onGalleryScroll"
          >
            <button
              v-for="(image, index) in product.images"
              :key="image.id ?? index"
              type="button"
              class="gallery-slide"
              :aria-label="`Ver imagen ${index + 1} de ${product.images.length} ampliada`"
              @click="openImageGallery(index)"
            >
              <img
                :src="buildImageVariantUrl(image.image_url, 800)"
                :srcset="buildImageSrcset(image.image_url, [400, 800])"
                sizes="(max-width: 1023px) 100vw, 50vw"
                :alt="`${product.name} - imagen ${index + 1}`"
                :loading="index === 0 ? 'eager' : 'lazy'"
                :fetchpriority="index === 0 ? 'high' : undefined"
                :decoding="index === 0 ? undefined : 'async'"
                width="800"
                height="1000"
                class="object-cover object-center w-full h-full"
              />
            </button>
            <img v-if="product.images.length === 0" src="/logo_redondo.jpg" :alt="product.name" class="gallery-slide object-cover" />
          </div>

          <span v-if="isOutOfStock" class="absolute px-3 py-1 text-xs font-bold text-white bg-gray-700 rounded top-3 left-3">SIN STOCK</span>
          <span v-else-if="product.has_discount && discountPercentage" class="absolute px-3 py-1 text-xs font-bold text-white bg-red-600 rounded top-3 left-3">-{{ discountPercentage }}%</span>

          <div v-if="product.images.length > 1" class="flex justify-center gap-1 mt-2 lg:hidden" role="tablist" aria-label="Elegir imagen">
            <button
              v-for="(image, index) in product.images"
              :key="image.id ?? index"
              type="button"
              class="gallery-dot"
              :aria-label="`Ir a la imagen ${index + 1}`"
              :aria-current="selectedImage === index ? 'true' : undefined"
              @click="goToImage(index)"
            ></button>
          </div>
        </div>

        <div v-if="product.images.length > 1" class="hidden gap-2 mt-3 lg:flex lg:flex-col lg:mt-0 lg:w-20">
          <button
            v-for="(image, index) in product.images"
            :key="image.id ?? index"
            type="button"
            class="w-20 h-20 overflow-hidden bg-gray-100 border-2 rounded-md"
            :class="selectedImage === index ? 'border-black' : 'border-transparent hover:border-gray-300'"
            :aria-label="`Ir a la imagen ${index + 1}`"
            @click="goToImage(index)"
          >
            <img :src="buildImageVariantUrl(image.image_url, 400)" alt="" loading="lazy" decoding="async" width="80" height="80" class="object-cover w-full h-full" />
          </button>
        </div>
      </section>

      <!-- Información -->
      <section class="px-4 pt-5 pb-8 lg:pt-0">
        <h1 class="text-2xl font-light text-gray-900 font-heading">{{ product.name }}</h1>

        <div class="mt-3">
          <div v-if="product.has_discount && product.discounted_price" class="flex flex-wrap items-baseline gap-x-3">
            <span class="text-3xl font-medium text-gray-900">{{ formatPrice(finalPrice) }}</span>
            <span class="text-lg text-gray-500 line-through">{{ formatPrice(product.price) }}</span>
          </div>
          <span v-else class="text-3xl font-medium text-gray-900">{{ formatPrice(finalPrice) }}</span>
          <p v-if="MERCADOPAGO_HABILITADO && installments > 1" class="mt-1 text-sm text-gray-700">
            {{ installments }} x {{ formatPrice(Math.round(finalPrice / installments)) }} sin interés
          </p>
        </div>

        <div v-if="availableColors.length > 0" class="mt-6">
          <h3 class="mb-2 text-sm font-medium text-gray-900">Color: <span class="font-normal text-gray-600">{{ selectedColor?.name }}</span></h3>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="color in availableColors"
              :key="color.id"
              type="button"
              @click="selectColor(color)"
              :disabled="!isColorAvailable(color)"
              class="min-h-12 min-w-12 px-4 py-2 text-sm font-medium transition-colors border rounded-md disabled:cursor-not-allowed disabled:text-gray-400 disabled:line-through disabled:bg-gray-50"
              :class="selectedColor?.id === color.id
                ? 'border-black bg-black text-white'
                : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'"
            >
              <span
                v-if="color.hex_code"
                class="inline-block w-3.5 h-3.5 mr-2 -ml-1 align-middle border border-gray-300 rounded-full"
                :style="{ backgroundColor: color.hex_code }"
              ></span>
              {{ color.name }}
            </button>
          </div>
        </div>

        <div v-if="availableSizes.length > 0" class="mt-5">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-900">Talle: <span class="font-normal text-gray-600">{{ selectedSize?.name }}</span></h3>
            <router-link to="/size-guide" class="text-sm text-gray-600 underline hover:text-gray-900">Guía de talles</router-link>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="size in availableSizes"
              :key="size.id"
              type="button"
              @click="selectedSize = size"
              :disabled="!isSizeAvailable(size)"
              class="min-h-12 min-w-[3rem] px-4 py-2 text-sm font-medium transition-colors border rounded-md disabled:cursor-not-allowed disabled:text-gray-400 disabled:line-through disabled:bg-gray-50"
              :class="selectedSize?.id === size.id
                ? 'border-black bg-black text-white'
                : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'"
            >
              {{ size.name }}
            </button>
          </div>
        </div>

        <p v-if="selectedVariant" class="mt-4 text-sm text-gray-600">Stock disponible: {{ selectedVariant.stock }}</p>
        <p v-else-if="product.is_unique && !isOutOfStock" class="mt-4 text-sm text-gray-600">Stock disponible: {{ product.stock }}</p>

        <div class="mt-5">
          <h3 class="mb-2 text-sm font-medium text-gray-900">Cantidad</h3>
          <div class="flex items-center w-40 border border-gray-300 rounded-md">
            <button type="button" aria-label="Disminuir cantidad" @click="decrementQuantity" :disabled="quantity <= 1"
              class="min-h-12 min-w-12 px-3 py-2 text-gray-700 disabled:text-gray-300 disabled:cursor-not-allowed">-</button>
            <input v-model.number="quantity" @blur="clampQuantity" type="number" step="1" min="1" :max="maxQuantity ?? undefined" aria-label="Cantidad"
              class="flex-1 w-full min-w-0 px-1 py-2 text-center border-none focus:ring-0 focus:outline-none" />
            <button type="button" aria-label="Aumentar cantidad" @click="incrementQuantity" :disabled="quantity >= (maxQuantity ?? 1)"
              class="min-h-12 min-w-12 px-3 py-2 text-gray-700 disabled:text-gray-300 disabled:cursor-not-allowed">+</button>
          </div>
        </div>

        <button
          type="button"
          @click="addToCart"
          :disabled="!canAddToCart"
          class="flex items-center justify-center w-full gap-2 px-6 py-4 mt-5 text-sm font-medium tracking-wide text-white uppercase bg-black rounded-md hover:bg-gray-800 disabled:bg-gray-700 disabled:cursor-not-allowed"
        >
          <template v-if="justAdded">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
            <span role="status">Agregado</span>
          </template>
          <template v-else>{{ buttonText }}</template>
        </button>

        <div class="flex flex-col gap-3 mt-5 text-sm text-gray-800">
          <button type="button" class="flex items-center min-h-12 gap-2 underline text-start" @click="paymentDialog?.showModal()">
            <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Z" /></svg>
            Medios de pago
          </button>
          <button type="button" class="flex items-center min-h-12 gap-2 underline text-start" @click="pickupDialog?.showModal()">
            <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" /></svg>
            Retiro en el local
          </button>
        </div>

        <div v-if="product.description" class="pt-5 mt-6 border-t border-gray-200">
          <h3 class="mb-2 text-sm font-medium text-gray-900">Descripción</h3>
          <div class="text-sm leading-relaxed text-gray-700" v-html="product.description"></div>
        </div>

        <button type="button" class="flex items-center justify-center w-full gap-2 px-4 py-3 mt-6 text-sm font-medium text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50" @click="shareProduct">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" /></svg>
          Compartir
        </button>
      </section>
    </div>

    <div v-else-if="!loading" class="flex items-center justify-center min-h-[50vh]">
      <div class="text-center">
        <h1 class="text-xl text-gray-900">Producto no encontrado</h1>
        <router-link to="/shop" class="inline-flex items-center min-h-12 underline">Volver a la tienda</router-link>
      </div>
    </div>

    <!-- Productos similares -->
    <section v-if="similarProducts.length > 0" class="py-10 mt-4 bg-gray-50" aria-labelledby="similares-titulo">
      <div class="max-w-6xl mx-auto">
        <h2 id="similares-titulo" class="px-4 mb-5 text-xl font-light text-gray-900 lg:px-8 font-heading">Productos similares</h2>
        <ul class="similar-track px-4 lg:px-8">
          <li v-for="similar in similarProducts" :key="similar.id" class="similar-item">
            <router-link :to="`/product/${similar.id}/${similar.name}`" class="block">
              <div class="overflow-hidden bg-gray-100 rounded-md aspect-[4/5]">
                <img :src="getSimilarProductImage(similar)" :alt="similar.name" loading="lazy" decoding="async" width="400" height="500" class="object-cover w-full h-full" />
              </div>
              <h3 class="mt-2 text-sm text-gray-900 truncate">{{ similar.name }}</h3>
              <p class="text-sm font-medium text-gray-900">{{ formatPrice(similar.discounted_price ?? similar.price) }}</p>
              <p v-if="MERCADOPAGO_HABILITADO && (similar.max_installments ?? 1) > 1" class="text-xs text-gray-600">
                {{ similar.max_installments }} x {{ formatPrice(Math.round((similar.discounted_price ?? similar.price) / (similar.max_installments ?? 1))) }} sin interés
              </p>
            </router-link>
          </li>
        </ul>
      </div>
    </section>

    <!-- WhatsApp flotante -->
    <a
      v-if="product"
      :href="whatsappUrl"
      target="_blank"
      rel="noopener"
      class="fixed z-30 flex items-center justify-center text-white bg-[#25D366] rounded-full shadow-lg w-14 h-14 bottom-24 right-6 hover:brightness-95"
      aria-label="Consultar por WhatsApp"
    >
      <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.309z"/></svg>
    </a>

    <!-- Diálogos nativos -->
    <dialog ref="paymentDialog" closedby="any" aria-labelledby="pago-titulo" class="info-dialog" @click="closeOnBackdrop">
      <h2 id="pago-titulo" class="text-lg font-medium text-gray-900">Medios de pago</h2>
      <ul class="mt-3 space-y-3 text-sm text-gray-700">
        <li v-if="MERCADOPAGO_HABILITADO"><strong>Mercado Pago:</strong> tarjetas de crédito y débito, dinero en cuenta<span v-if="installments > 1"> y hasta {{ installments }} cuotas sin interés</span>.</li>
        <li><strong>Transferencia bancaria:</strong> al finalizar la compra te enviamos los datos para transferir.</li>
      </ul>
      <form method="dialog" class="mt-5"><button class="dialog-close" autofocus>Cerrar</button></form>
    </dialog>

    <dialog ref="pickupDialog" closedby="any" aria-labelledby="retiro-titulo" class="info-dialog" @click="closeOnBackdrop">
      <h2 id="retiro-titulo" class="text-lg font-medium text-gray-900">Retiro en el local</h2>
      <p class="mt-3 text-sm text-gray-700">
        Todas las compras se retiran sin costo en
        <a :href="STORE_MAPS_URL" target="_blank" rel="noopener noreferrer" class="underline text-gray-900 hover:text-gray-600">{{ STORE_PICKUP_ADDRESS }}</a>.
        {{ STORE_PICKUP_HOURS }}.
      </p>
      <p class="mt-2 text-xs text-gray-600">Cambios dentro de los 7 días hábiles posteriores al retiro.</p>
      <a :href="whatsappUrl" target="_blank" rel="noopener" class="block mt-3 text-sm underline text-gray-900">Coordinar por WhatsApp</a>
      <form method="dialog" class="mt-5"><button class="dialog-close" autofocus>Cerrar</button></form>
    </dialog>

    <dialog ref="shareDialog" closedby="any" aria-labelledby="compartir-titulo" class="info-dialog" @click="closeOnBackdrop">
      <h2 id="compartir-titulo" class="text-lg font-medium text-gray-900">Compartir</h2>
      <div class="flex flex-col gap-2 mt-3 text-sm">
        <a :href="`https://wa.me/?text=${encodeURIComponent(`${product?.name ?? ''} ${pageUrl}`)}`" target="_blank" rel="noopener" class="px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50">WhatsApp</a>
        <button type="button" class="px-4 py-3 border border-gray-300 rounded-md text-start hover:bg-gray-50" @click="copyLink">Copiar enlace</button>
      </div>
      <form method="dialog" class="mt-5"><button class="dialog-close">Cerrar</button></form>
    </dialog>

    <ImageGalleryModal
      :is-open="showImageGallery"
      :images="product?.images || []"
      :initial-index="galleryInitialIndex"
      :alt="product?.name || ''"
      :shared-selector="'.product-main-image'"
      @close="closeImageGallery"
    />
  </div>
</template>

<style scoped>
.gallery-track {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
  touch-action: pan-x pan-y;
}
.gallery-track::-webkit-scrollbar { display: none; }
.gallery-slide {
  flex: 0 0 100%;
  scroll-snap-align: center;
  aspect-ratio: 4 / 5;
  cursor: zoom-in;
}
.gallery-slide:active { scale: 1; }
.gallery-dot {
  position: relative;
  width: 24px;
  height: 24px;
  background: none;
}
.gallery-dot::before {
  content: '';
  position: absolute;
  inset: 8px;
  border-radius: 9999px;
  background: #9ca3af;
  transition: all 0.2s;
}
.gallery-dot[aria-current='true']::before {
  background: #000;
  inset: 7px 4px;
}
.gallery-dot:focus-visible, .gallery-track:focus-visible { outline: 2px solid #000; outline-offset: 2px; }
.similar-track {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  overscroll-behavior-x: contain;
  scroll-padding-inline: 1rem;
  padding-bottom: 0.5rem;
  list-style: none;
  margin: 0;
}
.similar-item {
  flex: 0 0 44%;
  max-width: 14rem;
  scroll-snap-align: start;
}
@media (min-width: 1024px) {
  .similar-item { flex-basis: 22%; }
}
@media (prefers-reduced-motion: no-preference) {
  .gallery-track { scroll-behavior: smooth; }
}
.info-dialog {
  width: min(92vw, 26rem);
  padding: 1.5rem;
  border: 0;
  border-radius: 0.75rem;
  margin: auto;
  overscroll-behavior: contain;
}
.info-dialog::backdrop {
  background: rgb(0 0 0 / 0.5);
  overflow: hidden;
  overscroll-behavior: contain;
}
.dialog-close {
  width: 100%;
  padding: 0.75rem 1rem;
  color: #fff;
  background: #000;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}
</style>

<script setup lang="ts">
import { formatPrice } from '../../utils/price'
import { applySeo, productSeo, routeSeo } from '../../utils/seo'
import { buildImageVariantUrl, buildImageSrcset } from '../../utils/imageUrl'
import { ref, computed, watch } from 'vue';
import ImageGalleryModal from '../ui/ImageGalleryModal.vue';
import { useRoute } from 'vue-router';
import type { Product, ProductVariant, VariantOption } from '../../types/products/product.types';
import type { Color } from '../../types/products/color.types';
import type { Size } from '../../types/products/size.types';
import { useCartStore } from '../../store/cart';
import { productsApi, masterDataApi } from '../../config/index';
import { useToast } from 'vue-toastification';

const route = useRoute();
const product = ref<Product | null>(null);
const selectedImage = ref(0);
const selectedColor = ref<VariantOption | null>(null);
const selectedSize = ref<VariantOption | null>(null);
const quantity = ref(1);
const loading = ref(true);
const justAdded = ref(false);
let justAddedTimer: number | undefined;
const allColors = ref<Color[]>([]);
const allSizes = ref<Size[]>([]);
const similarProducts = ref<Product[]>([]);
const cartStore = useCartStore();
const toast = useToast();

// Image Gallery Modal states
const showImageGallery = ref(false);
const galleryInitialIndex = ref(0);

// Share functionality states

const galleryTrack = ref<HTMLElement | null>(null);
const paymentDialog = ref<HTMLDialogElement | null>(null);
const pickupDialog = ref<HTMLDialogElement | null>(null);
const shareDialog = ref<HTMLDialogElement | null>(null);

import { MERCADOPAGO_HABILITADO, WHATSAPP_NUMBER } from '../../config/payments';
import { STORE_MAPS_URL, STORE_PICKUP_ADDRESS, STORE_PICKUP_HOURS } from '../../config/store';

const finalPrice = computed(() => product.value?.has_discount && product.value.discounted_price ? product.value.discounted_price : product.value?.price ?? 0);
const installments = computed(() => product.value?.max_installments ?? 1);
const pageUrl = computed(() => window.location.href);
const whatsappUrl = computed(() =>
  `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(`Hola! Quiero consultar por ${product.value?.name ?? ''}`)}`
);

const onGalleryScroll = () => {
  const el = galleryTrack.value;
  if (el && el.clientWidth) selectedImage.value = Math.round(el.scrollLeft / el.clientWidth);
};

const goToImage = (index: number) => {
  const el = galleryTrack.value;
  if (!el) return;
  selectedImage.value = index;
  el.scrollTo({ left: index * el.clientWidth });
};

const closeOnBackdrop = (e: MouseEvent) => {
  const dialog = e.currentTarget as HTMLDialogElement;
  if (e.target !== dialog) return;
  const r = dialog.getBoundingClientRect();
  if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close();
};

// La API devuelve color/talle como texto (v.color, v.talle); si trae ids, se usan
const colorKey = (v: ProductVariant) => v.color ?? v.color_id;
const sizeKey = (v: ProductVariant) => v.talle ?? v.size_id;

const normalizeName = (n: string) => n.normalize('NFD').replace(/\p{Diacritic}/gu, '').trim().toLowerCase();

const buildOptions = (
  keys: Array<string | number | undefined>,
  master: Array<{ id: number; name: string; hex_code?: string }>
): VariantOption[] => {
  const unique = [...new Set(keys.filter((k): k is string | number => k !== undefined && k !== null && k !== ''))];
  return unique.map(key => {
    const match = master.find(m => m.id === key || normalizeName(m.name) === normalizeName(String(key)));
    return {
      id: key,
      name: typeof key === 'string' ? key : (match?.name ?? String(key)),
      hex_code: match?.hex_code
    };
  });
};

// Available colors from product variants
const availableColors = computed<VariantOption[]>(() => {
  if (!product.value?.variants || product.value.is_unique) return [];
  return buildOptions(product.value.variants.map(colorKey), allColors.value);
});

// Available sizes from product variants
const availableSizes = computed<VariantOption[]>(() => {
  if (!product.value?.variants || product.value.is_unique) return [];
  return buildOptions(product.value.variants.map(sizeKey), allSizes.value);
});

// Selected variant based on color and size selection
const selectedVariant = computed(() => {
  if (!product.value?.variants || product.value.is_unique) return null;
  if (!selectedColor.value || !selectedSize.value) return null;
  
  return product.value.variants.find(v => 
    colorKey(v) === selectedColor.value?.id && sizeKey(v) === selectedSize.value?.id
  ) ?? null;
});

// Solo existen como válidas las combinaciones que son variantes con stock
const isColorAvailable = (color: VariantOption) =>
  !!product.value?.variants.some(v => colorKey(v) === color.id && v.stock > 0);

const isSizeAvailable = (size: VariantOption) =>
  !!product.value?.variants.some(v =>
    sizeKey(v) === size.id &&
    (!selectedColor.value || colorKey(v) === selectedColor.value.id) &&
    v.stock > 0
  );

const selectColor = (color: VariantOption) => {
  selectedColor.value = color;
  if (selectedSize.value && !isSizeAvailable(selectedSize.value)) {
    const first = product.value?.variants.find(v => colorKey(v) === color.id && v.stock > 0);
    const size = first && availableSizes.value.find(s => s.id === sizeKey(first));
    selectedSize.value = size ?? null;
  }
};

watch(selectedVariant, () => {
  quantity.value = 1;
});

// Check if can add to cart
const canAddToCart = computed(() => {
  if (!product.value || !Number.isInteger(quantity.value) || quantity.value < 1 || quantity.value > maxQuantity.value) return false;

  // For unique products (no variants)
  if (product.value.is_unique) {
    return (product.value.stock ?? 0) > 0;
  }
  
  // For products with variants
  if (selectedVariant.value) {
    return selectedVariant.value.stock > 0;
  }
  
  return false;
});

// Maximum quantity available
const maxQuantity = computed(() => {
  if (!product.value) return 1;
  
  if (product.value.is_unique) {
    return product.value.stock ?? 0;
  }
  
  if (selectedVariant.value) {
    return selectedVariant.value.stock;
  }
  
  return 1;
});

// Button text based on state
const buttonText = computed(() => {
  if (!product.value) return 'Cargando...';
  
  if (product.value.is_unique) {
    return (product.value.stock ?? 0) > 0 ? 'Agregar al carrito' : 'Sin stock';
  }
  
  if (!selectedColor.value || !selectedSize.value) {
    return 'Selecciona color y talle';
  }
  
  if (selectedVariant.value) {
    return selectedVariant.value.stock > 0 ? 'Agregar al carrito' : 'Sin stock';
  }
  
  return 'No disponible';
});

// Determinar si el producto está sin stock
const isOutOfStock = computed(() => {
  if (!product.value) return false;

  // Para productos unicos (is_unique = true), verificar el stock directo
  if (product.value.is_unique) {
    return (product.value.stock ?? 0) === 0;
  }
  
  // Para productos con variantes, verificar si todas las variantes tienen stock 0
  if (product.value.variants && product.value.variants.length > 0) {
    return product.value.variants.every(variant => variant.stock === 0);
  }
  
  // Si no hay variantes y no es unico, asumir que está disponible
  return false;
});

// Calculate discount percentage
const discountPercentage = computed(() => {
  if (!product.value || !product.value.has_discount || !product.value.discount_amount) {
    return 0;
  }
  
  return Math.round((product.value.discount_amount / product.value.price) * 100);
});

const clampQuantity = () => {
  const value = Number(quantity.value);
  quantity.value = Math.min(Math.max(1, Math.floor(Number.isFinite(value) ? value : 1)), Math.max(1, maxQuantity.value));
};

// Quantity functions
const incrementQuantity = () => {
  if (quantity.value < (maxQuantity.value ?? 1)) {
    quantity.value++;
  }
};

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--;
  }
};

// Function to get similar product image
const getSimilarProductImage = (product: Product) => {
  const defaultImage = '/logo_redondo.jpg';
  
  if (product.images && product.images[0]) {
    return product.images[0].image_url;
  }
  return defaultImage;
};

// Misma categoría primero; si faltan, se completa con otros productos (máx. 6)
const loadSimilarProducts = (all: Product[], current: Product) => {
  const others = all.filter(p => p.id !== current.id);
  const sameCategory = others.filter(p => p.categoria === current.categoria);
  const rest = others.filter(p => p.categoria !== current.categoria);
  similarProducts.value = [...sameCategory, ...rest].slice(0, 6);
};

watch(() => route.params.id, async (id, _oldId, onCleanup) => {
  if (!id) return;
  let cancelled = false;
  onCleanup(() => { cancelled = true; });
  product.value = null;
  selectedColor.value = null;
  selectedSize.value = null;
  quantity.value = 1;
  selectedImage.value = 0;
  loading.value = true;
  const productId = Number(id);
  try {
    // Load all products and find by ID
    const response = await productsApi.getProducts();
    const foundProduct = response.products.find((p: Product) => p.id === productId);
    
    if (cancelled) return;
    if (!foundProduct) {
      applySeo({ ...routeSeo(route.path, true), title: 'Prenda no encontrada | Showroom Isabella' });
      return;
    }
    
    product.value = foundProduct;
    applySeo(productSeo(foundProduct, !['pro', 'production'].includes(import.meta.env.MODE)));
    
    // Load colors and sizes for variants
    if (product.value && !product.value.is_unique && product.value.variants) {
      try {
        const [colorsResponse, sizesResponse] = await Promise.all([
          masterDataApi.getColors(),
          masterDataApi.getSizes()
        ]);
        if (cancelled) return;
        allColors.value = colorsResponse;
        allSizes.value = sizesResponse;
      } catch (error) {
        // El maestro solo aporta hex_code; sin él se usan los textos de las variantes
      }
      
      if (cancelled) return;
      // Auto-select first combination with stock
      const firstInStock = product.value.variants.find(v => v.stock > 0);
      if (firstInStock) {
        selectedColor.value = availableColors.value.find(c => c.id === colorKey(firstInStock)) ?? null;
        selectedSize.value = availableSizes.value.find(s => s.id === sizeKey(firstInStock)) ?? null;
      }
    }

    // Load similar products by category
    if (product.value) {
      loadSimilarProducts(response.products, product.value);
    }
  } catch (error) {
    console.error('No se pudo cargar la prenda', error);
    if (!cancelled) applySeo({ ...routeSeo(route.path, true), title: 'Prenda no disponible | Showroom Isabella' });
  } finally {
    if (!cancelled) loading.value = false;
  }
}, { immediate: true });

watch(() => route.fullPath, () => {
  if (product.value && product.value.id === Number(route.params.id)) {
    applySeo(productSeo(product.value, !['pro', 'production'].includes(import.meta.env.MODE)));
  }
}, { flush: 'post' });

const addToCart = () => {
  if (!product.value) {
    return;
  }
  
  if (!canAddToCart.value) {
    // Check why we can't add to cart and show appropriate message
    if (product.value.is_unique) {
      if ((product.value.stock ?? 0) <= 0) {
        toast.warning('Este producto no tiene stock disponible');
      }
    } else {
      if (!selectedColor.value || !selectedSize.value) {
        toast.warning('Por favor selecciona color y talle');
      } else if (!selectedVariant.value || selectedVariant.value.stock <= 0) {
        toast.warning('La combinación seleccionada no tiene stock disponible');
      }
    }
    return;
  }
  
  try {
    // For unique products
    if (product.value.is_unique) {
      cartStore.addToCart(
        product.value,
        quantity.value,
        undefined,
        {
          color: selectedColor.value || undefined,
          size: selectedSize.value || undefined
        }
      );
    } else {
      // For products with variants
      if (selectedVariant.value && selectedColor.value && selectedSize.value) {
        cartStore.addToCart(
          product.value,
          Math.min(Math.max(1, quantity.value || 1), selectedVariant.value.stock),
          {
            variant: selectedVariant.value,
            color: selectedColor.value,
            size: selectedSize.value
          }
        );
      } else {
        toast.warning('Por favor selecciona color y talle');
        return;
      }
    }
    
    // Reset quantity to 1 after adding to cart
    quantity.value = 1;
    justAdded.value = true;
    clearTimeout(justAddedTimer);
    justAddedTimer = window.setTimeout(() => { justAdded.value = false; }, 1500);
    
  } catch (error) {
    toast.error('Error al agregar el producto al carrito');
  }
};

// Image Gallery Modal functions
const openImageGallery = (index: number) => {
  galleryInitialIndex.value = index;
  showImageGallery.value = true;
  // Prevent body scroll
  document.body.style.overflow = 'hidden';
};

const closeImageGallery = () => {
  showImageGallery.value = false;
  // Restore body scroll
  document.body.style.overflow = 'auto';
};

const copyLink = async () => {
  await navigator.clipboard.writeText(window.location.href);
  toast.success('¡Enlace copiado al portapapeles!');
  shareDialog.value?.close();
};

const shareProduct = async () => {
  if (!navigator.share) {
    shareDialog.value?.showModal();
    return;
  }
  try {
    await navigator.share({ title: product.value?.name, url: window.location.href });
  } catch {
    // el usuario canceló el diálogo nativo
  }
};
</script>
