<template>
  <div class="min-h-screen bg-white">
    <!-- Breadcrumb Navigation -->
    <nav class="px-4 py-4 mx-auto max-w-7xl lg:px-8" aria-label="Breadcrumb">
      <ol class="flex items-center space-x-2 text-sm font-body">
        <li>
          <router-link to="/" class="text-gray-500 transition-colors hover:text-gray-700">
            Home
          </router-link>
        </li>
        <li class="text-gray-400">/</li>
        <li>
          <router-link to="/shop" class="text-gray-500 transition-colors hover:text-gray-700">
            Shop
          </router-link>
        </li>
        <li v-if="product" class="text-gray-400">/</li>
        <li v-if="product" class="max-w-xs font-medium text-gray-900 truncate">
          {{ product.name }}
        </li>
      </ol>
    </nav>
    
    <div v-if="product" class="mx-auto max-w-7xl">
      <!-- Desktop Layout -->
      <div class="hidden lg:flex lg:gap-x-12 lg:px-8 lg:py-8 lg:max-w-6xl lg:mx-auto">
        <!-- Left Side - Images (mÃ¡s compacto) -->
        <div class="flex flex-shrink-0 gap-4">
          <!-- Main Image (mÃ¡s grande) -->
          <div class="product-main-image w-[26rem] h-[32rem] overflow-hidden bg-gray-100 rounded-lg flex-shrink-0 border-4 border-white shadow-lg ring-1 ring-gray-200 relative cursor-pointer" @click="openImageGallery(selectedImage)">
            <OptimizedImage
              :src="mainImage"
              :alt="product.name"
              loading="eager"
              :show-spinner="true"
              :fallback-src="'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a'"
              image-class="object-cover object-center w-full h-full"
            />
            <!-- Sin Stock Overlay Desktop -->
            <div v-if="isOutOfStock" class="absolute top-0 left-0 z-10 mt-2 ml-4">
              <span class="px-3 py-1 text-xs font-bold text-white bg-gray-600 rounded-lg">SIN STOCK</span>
            </div>
            
            <!-- Discount Badge Desktop -->
            <div v-else-if="product.has_discount && product.discount_amount" class="absolute top-0 right-0 z-10 mt-2 mr-4">
              <div class="px-3 py-1 text-xs font-bold text-white bg-red-600 rounded-lg">
                -{{ discountPercentage }}% OFF
              </div>
            </div>
          </div>
          
          <!-- Thumbnail Images (mÃ¡s grandes) -->
          <div class="flex flex-col w-20 gap-2">
            <div 
              v-for="(image, index) in product.images" 
              :key="index"
              @click="selectedImage = index; openImageGallery(index)"
              class="w-20 h-20 overflow-hidden transition-colors bg-gray-100 border-2 rounded-md cursor-pointer"
              :class="selectedImage === index ? 'border-black' : 'border-transparent hover:border-gray-300'"
            >
              <OptimizedImage
                :src="image.image_url"
                :alt="`${product.name} - imagen ${index + 1}`"
                loading="lazy"
                aspect-ratio="square"
                :show-spinner="true"
                image-class="object-cover object-center w-full h-full"
              />
            </div>
          </div>
        </div>

        <!-- Right Side - Product Info (mÃ¡s cerca) -->
        <div class="flex-1 pl-6">
          <!-- Product Title -->
          <h1 class="mb-2 text-2xl font-light text-gray-900 font-heading">{{ product.name }}</h1>
          
          <!-- Price -->
          <div class="mb-6">
            <div v-if="product.has_discount && product.discounted_price" class="flex items-center space-x-3">
              <span class="text-2xl font-light text-red-600 font-body">${{ product.discounted_price.toLocaleString() }}</span>
              <span class="text-lg font-light text-gray-500 line-through font-body">${{ product.price.toLocaleString() }}</span>
              <span class="px-2 py-1 text-xs font-bold text-red-800 bg-red-100 rounded-full">
                {{ discountPercentage }}% OFF
              </span>
            </div>
            <div v-else>
              <span class="text-2xl font-light text-gray-900 font-body">${{ product.price.toLocaleString() }}</span>
            </div>
          </div>

          <!-- Color Selection -->
          <div v-if="availableColors.length > 0" class="mb-6">
            <h3 class="mb-3 text-sm font-medium text-gray-900 font-heading">Color</h3>
            <div class="flex space-x-3">
              <button
                v-for="color in availableColors"
                :key="color.id"
                @click="selectedColor = color"
                class="w-8 h-8 transition-colors border-2 rounded-full"
                :class="selectedColor?.id === color.id ? 'border-black' : 'border-gray-300'"
                :style="{ backgroundColor: color.hex_code }"
                :title="color.name"
              ></button>
            </div>
          </div>

          <!-- Size Selection -->
          <div v-if="availableSizes.length > 0" class="mb-6">
            <h3 class="mb-3 text-sm font-medium text-gray-900 font-heading">Talle</h3>
            <div class="grid grid-cols-4 gap-3">
              <button
                v-for="size in availableSizes"
                :key="size.id"
                @click="selectedSize = size"
                class="px-4 py-2 text-sm font-medium transition-colors border rounded-md font-body"
                :class="selectedSize?.id === size.id 
                  ? 'border-black bg-black text-white' 
                  : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'"
              >
                {{ size.name }}
              </button>
            </div>
          </div>

          <!-- Stock Info -->
          <div v-if="selectedVariant" class="mb-6">
            <p class="text-sm text-gray-600 font-body">
              Stock disponible: {{ selectedVariant.stock }}
            </p>
          </div>

          <!-- Quantity and Add to Cart -->
          <div class="mb-6">
            <!-- Quantity Selector -->
            <div class="mb-4">
              <h3 class="mb-2 text-sm font-medium text-gray-900 font-heading">Cantidad</h3>
              <div class="flex items-center w-32 border border-gray-300 rounded-md">
                <button 
                  @click="decrementQuantity"
                  :disabled="quantity <= 1"
                  class="px-3 py-2 text-gray-600 font-body hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                >
                  -
                </button>
                <input 
                  v-model.number="quantity"
                  type="number"
                  min="1"
                  :max="maxQuantity ?? undefined"
                  class="flex-1 px-2 py-2 text-center border-none font-body focus:ring-0 focus:outline-none"
                />
                <button 
                  @click="incrementQuantity"
                  :disabled="quantity >= (maxQuantity ?? 1)"
                  class="px-3 py-2 text-gray-600 font-body hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                >
                  +
                </button>
              </div>
            </div>

            <!-- Add to Cart Button -->
            <button 
              @click="addToCart"
              :disabled="!canAddToCart"
              class="w-full px-6 py-3 text-sm font-medium transition-colors rounded-md "
              :class="canAddToCart 
                ? 'bg-black text-white hover:bg-gray-800' 
                : 'bg-gray-700 text-white cursor-not-allowed'"
            >
              {{ buttonText }}
            </button>
          </div>

          <!-- Product Description -->
          <div class="space-y-4">
            <h3 class="text-sm font-medium text-gray-900 font-body">Descripción:</h3>
            <div class="text-sm font-normal leading-tight text-gray-800" v-html="product.description"></div>
          </div>

          <!-- Product Details -->
          <div class="mt-8 space-y-2">
            <div class="flex">
              <span class="w-24 text-sm font-medium text-gray-900 font-body">Categoría:</span>
              <span class="text-sm text-gray-600 font-body">{{ product.categoria }}</span>
            </div>
            <div class="flex">
              <span class="w-24 text-sm font-medium text-gray-900 font-body">Género:</span>
              <span class="text-sm text-gray-600 font-body">{{ product.genero }}</span>
            </div>
            <div class="flex">
              <span class="w-24 text-sm font-medium text-gray-900 font-body">Estado:</span>
              <span class="text-sm text-gray-600 font-body">{{ product.estado }}</span>
            </div>
          </div>

          <!-- Share Button Desktop -->
          <div class="relative mt-6">
            <button
              @click="toggleShareDropdown"
              class="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-gray-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              Compartir producto
            </button>
            
            <!-- Dropdown -->
            <div v-if="showShareDropdown" class="absolute right-0 z-10 w-48 mt-2 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
              <div class="py-1">
                <button @click="shareProduct('whatsapp')" class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg class="w-4 h-4 mr-3 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.309z"/>
                  </svg>
                  WhatsApp
                </button>
                <button @click="shareProduct('instagram')" class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg class="w-4 h-4 mr-3 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                  Instagram
                </button>
                <button @click="shareProduct('facebook')" class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg class="w-4 h-4 mr-3 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  Facebook
                </button>
                <button @click="shareProduct('x')" class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg class="w-4 h-4 mr-3 text-black" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                  X
                </button>
                <button @click="shareProduct('copy')" class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                  <svg class="w-4 h-4 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copiar enlace
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mobile Layout -->
      <div class="lg:hidden">
        <!-- Mobile Images -->
        <div class="px-4 py-6">
          <div class="relative mb-4 overflow-hidden bg-gray-100 rounded-lg cursor-pointer product-main-image" style="aspect-ratio: 26/32;" @click="openImageGallery(selectedImage)">
            <OptimizedImage
              :src="mainImage"
              :alt="product.name"
              loading="eager"
              :show-spinner="true"
              :fallback-src="'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a'"
              image-class="object-cover object-center w-full h-full"
            />
            <!-- Sin Stock Overlay Mobile -->
            <div v-if="isOutOfStock" class="absolute inset-0 flex items-center justify-center bg-black rounded-lg bg-opacity-40">
              <div class="px-4 py-2 bg-white rounded-lg bg-opacity-90">
                <span class="text-lg font-semibold text-gray-800 font-heading">Sin Stock</span>
              </div>
            </div>
            
            <!-- Discount Badge Mobile -->
            <div v-else-if="product.has_discount && product.discount_amount" class="absolute z-10 top-2 right-2">
              <div class="px-2 py-1 text-xs font-bold text-white bg-red-600 rounded-lg">
                -{{ discountPercentage }}%
              </div>
            </div>
          </div>
          
          <!-- Mobile Thumbnail Scroll -->
          <div class="flex pb-4 space-x-3 overflow-x-auto">
            <div 
              v-for="(image, index) in product.images" 
              :key="index"
              @click="selectedImage = index; openImageGallery(index)"
              class="flex-shrink-0 w-16 h-16 overflow-hidden transition-colors bg-gray-100 border-2 rounded-md cursor-pointer"
              :class="selectedImage === index ? 'border-black' : 'border-transparent'"
            >
              <OptimizedImage
                :src="image.image_url"
                :alt="`${product.name} - imagen ${index + 1}`"
                loading="lazy"
                aspect-ratio="square"
                :show-spinner="true"
                image-class="object-cover object-center w-full h-full"
              />
            </div>
          </div>
        </div>

        <!-- Mobile Product Info -->
        <div class="px-4 pb-8">
          <h1 class="mb-2 text-xl font-light text-gray-900 font-heading">{{ product.name }}</h1>
          <div class="mb-4">
            <div v-if="product.has_discount && product.discounted_price" class="flex items-center space-x-2">
              <span class="text-xl font-light text-red-600 font-body">${{ product.discounted_price.toLocaleString() }}</span>
              <span class="text-sm font-light text-gray-500 line-through font-body">${{ product.price.toLocaleString() }}</span>
              <span class="px-2 py-1 text-xs font-bold text-red-800 bg-red-100 rounded-full">
                {{ discountPercentage }}% OFF
              </span>
            </div>
            <div v-else>
              <span class="text-xl font-light text-gray-900 font-body">${{ product.price.toLocaleString() }}</span>
            </div>
          </div>

          <!-- Mobile Color Selection -->
          <div v-if="availableColors.length > 0" class="mb-4">
            <h3 class="mb-2 text-sm font-medium text-gray-900 font-heading">Color</h3>
            <div class="flex space-x-2">
              <button
                v-for="color in availableColors"
                :key="color.id"
                @click="selectedColor = color"
                class="w-6 h-6 transition-colors border-2 rounded-full"
                :class="selectedColor?.id === color.id ? 'border-black' : 'border-gray-300'"
                :style="{ backgroundColor: color.hex_code }"
              ></button>
            </div>
          </div>

          <!-- Mobile Size Selection -->
          <div v-if="availableSizes.length > 0" class="mb-4">
            <h3 class="mb-2 text-sm font-medium text-gray-900 font-heading">Talle</h3>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="size in availableSizes"
                :key="size.id"
                @click="selectedSize = size"
                class="px-2 py-1 text-xs font-medium transition-colors border rounded font-body"
                :class="selectedSize?.id === size.id 
                  ? 'border-black bg-black text-white' 
                  : 'border-gray-300 bg-white text-gray-900'"
              >
                {{ size.name }}
              </button>
            </div>
          </div>

          <!-- Mobile Quantity and Add to Cart -->
          <div class="mb-4">
            <!-- Mobile Quantity Selector -->
            <div class="mb-3">
              <h3 class="mb-2 text-sm font-medium text-gray-900 font-heading">Cantidad</h3>
              <div class="flex items-center border border-gray-300 rounded-md w-28">
                <button 
                  @click="decrementQuantity"
                  :disabled="quantity <= 1"
                  class="px-2 py-1 text-sm text-gray-600 font-body hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                >
                  -
                </button>
                <input 
                  v-model.number="quantity"
                  type="number"
                  min="1"
                  :max="maxQuantity ?? undefined"
                  class="flex-1 px-1 py-1 text-sm text-center border-none font-body focus:ring-0 focus:outline-none"
                />
                <button 
                  @click="incrementQuantity"
                  :disabled="quantity >= (maxQuantity ?? 1)"
                  class="px-2 py-1 text-sm text-gray-600 font-body hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                >
                  +
                </button>
              </div>
            </div>

            <!-- Mobile Add to Cart Button -->
            <button 
              @click="addToCart"
              :disabled="!canAddToCart"
              class="w-full px-6 py-3 text-sm font-medium transition-colors rounded-md "
              :class="canAddToCart 
                   ? 'bg-black text-white hover:bg-gray-700' 
                : 'bg-gray-700 text-white cursor-not-allowed'"
            >
              {{ buttonText }}
            </button>
          </div>

          <!-- Mobile Description -->
          <div class="space-y-3">
            <h3 class="text-sm font-medium text-gray-900 font-heading">Descripcin</h3>
            <div class="text-sm text-gray-600 font-body" v-html="product.description"></div>
          </div>

          <!-- Share Button Mobile -->
          <div class="mt-6">
            <button
              @click="openShareModal"
              class="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              Compartir producto
            </button>
          </div>
        </div>
      </div>

      <!-- Productos Similares Section -->
      <div v-if="similarProducts.length > 0" class="px-8 py-12 bg-gray-50">
        <div class="max-w-6xl mx-auto">
          <h2 class="mb-8 text-2xl font-light text-center text-gray-900 font-heading">Productos Similares</h2>
          
          <!-- Desktop Grid -->
          <div class="hidden md:grid md:grid-cols-4 md:gap-6">
            <div 
              v-for="similarProduct in similarProducts.slice(0, 4)" 
              :key="similarProduct.id"
              class="group"
            >
              <router-link :to="`/product/${similarProduct.id}/${similarProduct.name}`" class="block">
                <div class="relative overflow-hidden transition-shadow bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md">
                  <!-- Image -->
                  <div class="overflow-hidden bg-gray-100 aspect-square">
                    <img 
                      :src="getSimilarProductImage(similarProduct)" 
                      :alt="similarProduct.name"
                      loading="eager"
                      class="object-cover object-center w-full h-full transition-transform duration-300 group-hover:scale-105"
                    />
                  </div>
                  
                  <!-- Product Info -->
                  <div class="p-4">
                    <h3 class="text-sm font-medium text-gray-900 transition-colors font-heading group-hover:text-gray-700">
                      {{ similarProduct.name }}
                    </h3>
                    <p class="mt-1 text-sm font-medium text-gray-900 font-body">
                      ${{ similarProduct.price.toLocaleString() }}
                    </p>
                    <p v-if="similarProduct.categoria" class="mt-1 text-xs tracking-wide text-gray-500 uppercase font-body">
                      {{ similarProduct.categoria }}
                    </p>
                  </div>
                </div>
              </router-link>
            </div>
          </div>

          <!-- Mobile Scroll -->
          <div class="md:hidden">
            <div class="flex pb-4 space-x-4 overflow-x-auto">
              <div 
                v-for="similarProduct in similarProducts.slice(0, 6)" 
                :key="similarProduct.id"
                class="flex-shrink-0 w-48 group"
              >
                <router-link :to="`/product/${similarProduct.id}/${similarProduct.name}`" class="block">
                  <div class="relative overflow-hidden bg-white border border-gray-200 rounded-lg shadow-sm">
                    <!-- Image -->
                    <div class="overflow-hidden bg-gray-100 aspect-square">
                      <img 
                        :src="getSimilarProductImage(similarProduct)" 
                        :alt="similarProduct.name"
                        class="object-cover object-center w-full h-full"
                      />
                    </div>
                    
                    <!-- Product Info -->
                    <div class="p-3">
                      <h3 class="text-sm font-medium text-gray-900 truncate font-heading">
                        {{ similarProduct.name }}
                      </h3>
                      <p class="mt-1 text-sm font-medium text-gray-900 font-body">
                        ${{ similarProduct.price.toLocaleString() }}
                      </p>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="w-8 h-8 mx-auto mb-4 border-b-2 border-gray-600 rounded-full animate-spin"></div>
        <p class="text-gray-600 font-body">Cargando producto...</p>
      </div>
    </div>

    <!-- Share Modal Mobile -->
    <div v-if="showShareModal" class="fixed inset-0 z-50 overflow-y-auto" @click="closeShareOptions">
      <div class="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="closeShareOptions"></div>
        <div class="inline-block w-full max-w-sm p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl" @click.stop>
          <h3 class="mb-4 text-lg font-medium text-gray-900">Compartir producto</h3>
          <div class="space-y-3">
            <button @click="shareProduct('whatsapp')" class="flex items-center w-full px-4 py-3 text-sm text-gray-700 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 mr-3 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.309z"/>
              </svg>
              WhatsApp
            </button>
            <button @click="shareProduct('instagram')" class="flex items-center w-full px-4 py-3 text-sm text-gray-700 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 mr-3 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
              Instagram
            </button>
            <button @click="shareProduct('facebook')" class="flex items-center w-full px-4 py-3 text-sm text-gray-700 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 mr-3 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
            <button @click="shareProduct('x')" class="flex items-center w-full px-4 py-3 text-sm text-gray-700 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 mr-3 text-black" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
              X
            </button>
            <button @click="shareProduct('copy')" class="flex items-center w-full px-4 py-3 text-sm text-gray-700 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copiar enlace
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Gallery Modal -->
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import OptimizedImage from './OptimizedImage.vue';
import ImageGalleryModal from '../ui/ImageGalleryModal.vue';
import { useRoute } from 'vue-router';
import type { Product } from '../../types/products/product.types';
import type { Color } from '../../types/products/color.types';
import type { Size } from '../../types/products/size.types';
import { useCartStore } from '../../store/cart';
import { productsApi, masterDataApi } from '../../config/index';
import { useToast } from 'vue-toastification';

const route = useRoute();
const product = ref<Product | null>(null);
const selectedImage = ref(0);
const selectedColor = ref<Color | null>(null);
const selectedSize = ref<Size | null>(null);
const quantity = ref(1);
const allColors = ref<Color[]>([]);
const allSizes = ref<Size[]>([]);
const similarProducts = ref<Product[]>([]);
const cartStore = useCartStore();
const toast = useToast();

// Image Gallery Modal states
const showImageGallery = ref(false);
const galleryInitialIndex = ref(0);

// Share functionality states
const showShareDropdown = ref(false);
const showShareModal = ref(false);

// Computed properties
const mainImage = computed(() => {
  const defaultImage = 'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a';
  
  if (product.value?.images && product.value.images[selectedImage.value]) {
    return product.value.images[selectedImage.value].image_url;
  }
  return defaultImage;
});

// Available colors from product variants
const availableColors = computed(() => {
  if (!product.value?.variants || product.value.is_unique) return [];
  
  const colorIds = [...new Set(product.value.variants.map(v => v.color_id))];
  return allColors.value.filter(color => colorIds.includes(color.id));
});

// Available sizes from product variants
const availableSizes = computed(() => {
  if (!product.value?.variants || product.value.is_unique) return [];
  
  const sizeIds = [...new Set(product.value.variants.map(v => v.size_id))];
  return allSizes.value.filter(size => sizeIds.includes(size.id));
});

// Selected variant based on color and size selection
const selectedVariant = computed(() => {
  if (!product.value?.variants || product.value.is_unique) return null;
  if (!selectedColor.value || !selectedSize.value) return null;
  
  return product.value.variants.find(v => 
    v.color_id === selectedColor.value?.id && v.size_id === selectedSize.value?.id
  );
});

// Check if can add to cart
const canAddToCart = computed(() => {
  if (!product.value) return false;
  
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

// Determinar si el producto estÃ¡ sin stock
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
  
  // Si no hay variantes y no es unico, asumir que estÃ¡ disponible
  return false;
});

// Calculate discount percentage
const discountPercentage = computed(() => {
  if (!product.value || !product.value.has_discount || !product.value.discount_amount) {
    return 0;
  }
  
  return Math.round((product.value.discount_amount / product.value.price) * 100);
});

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
  const defaultImage = 'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a';
  
  if (product.images && product.images[0]) {
    return product.images[0].image_url;
  }
  return defaultImage;
};

// Function to load similar products
const loadSimilarProducts = async (categoria: string, currentProductId: number) => {
  try {
    const response = await productsApi.getProducts();
    
    // Filter products by same category, excluding current product
    const filtered = response.products.filter((p: Product) => 
      p.categoria === categoria && 
      p.id !== currentProductId &&
      p.estado === 'activo' // Only show active products
    );
    
    // Shuffle and take first 6 products
    const shuffled = filtered.sort(() => 0.5 - Math.random());
    similarProducts.value = shuffled.slice(0, 6);
  } catch (error) {
    similarProducts.value = [];
  }
};

onMounted(async () => {
  const productId = parseInt(route.params.id as string);
  try {
    // Load all products and find by ID
    const response = await productsApi.getProducts();
    const foundProduct = response.products.find((p: Product) => p.id === productId);
    
    if (!foundProduct) {
      return;
    }
    
    product.value = foundProduct;
    
    // Load colors and sizes for variants
    if (product.value && !product.value.is_unique && product.value.variants) {
      const [colorsResponse, sizesResponse] = await Promise.all([
        masterDataApi.getColors(),
        masterDataApi.getSizes()
      ]);
      allColors.value = colorsResponse;
      allSizes.value = sizesResponse;
      
      // Auto-select first available color and size if available
      if (availableColors.value.length > 0) {
        selectedColor.value = availableColors.value[0];
      }
      if (availableSizes.value.length > 0) {
        selectedSize.value = availableSizes.value[0];
      }
    }

    // Load similar products by category
    if (product.value && product.value.categoria) {
      await loadSimilarProducts(product.value.categoria, product.value.id);
    }
  } catch (error) {
  }
});

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
        toast.warning('La combinacin seleccionada no tiene stock disponible');
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
          quantity.value,
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

// Share functionality
const shareProduct = (platform: string) => {
  const productName = product.value?.name || '';
  const productURL = window.location.href;
  
  switch (platform) {
    case 'whatsapp':
      window.open(`whatsapp://send?text=${encodeURIComponent(productName + ' - ' + productURL)}`);
      break;
    case 'instagram':
      // Instagram doesn't have direct share API, use Web Share API or fallback
      if (navigator.share) {
        navigator.share({
          title: productName,
          url: productURL
        }).catch(() => {
          // Fallback if share fails
          navigator.clipboard.writeText(productURL);
          toast.info('Enlace copiado. Pégalo en Instagram para compartir.');
        });
      } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(productURL);
        toast.info('Enlace copiado. Pégalo en Instagram para compartir.');
      }
      break;
    case 'facebook':
      window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(productURL)}`);
      break;
    case 'x':
    case 'twitter': // Maintain compatibility
      window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(productName)}&url=${encodeURIComponent(productURL)}`);
      break;
    case 'copy':
      navigator.clipboard.writeText(productURL);
      toast.success('¡Enlace copiado al portapapeles!');
      break;
  }
  closeShareOptions();
};

const toggleShareDropdown = () => {
  showShareDropdown.value = !showShareDropdown.value;
};

const openShareModal = () => {
  showShareModal.value = true;
};

const closeShareOptions = () => {
  showShareDropdown.value = false;
  showShareModal.value = false;
};
</script>

