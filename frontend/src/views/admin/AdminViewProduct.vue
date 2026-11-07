<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow">
      <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Gestión de Productos</h1>
            <p class="mt-1 text-sm text-gray-500">Administra el catálogo de productos, variantes y existencias</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white border-b border-gray-200">
      <div class="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <nav class="flex -mb-px space-x-8">
          <router-link
            to="/admin/products"
            class="px-1 py-4 text-sm font-medium border-b-2"
            active-class="text-gray-800 border-gray-500"
            inactive-class="text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300"
          >
            Productos
          </router-link>
          <router-link
            to="/admin/users"
            class="px-1 py-4 text-sm font-medium border-b-2"
            active-class="text-gray-800 border-gray-500"
            inactive-class="text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300"
          >
            Usuarios
          </router-link>
          <router-link
            to="/admin/orders"
            class="px-1 py-4 text-sm font-medium border-b-2"
            active-class="text-gray-800 border-gray-500"
            inactive-class="text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300"
          >
            Pedidos
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">

    <!-- Layout de dos columnas: Formulario + Vista previa -->
    <div class="grid grid-cols-1 gap-8 mb-8 lg:grid-cols-12">
      <!-- Formulario (8 columnas) -->
      <div class="lg:col-span-8">
        <form @submit.prevent="confirmSave" class="p-8 bg-white border-2 border-gray-200 shadow-lg rounded-xl">
          <h2 class="mb-6 text-2xl font-bold text-gray-800">{{ editing ? 'Editar Producto' : 'Nuevo Producto' }}</h2>

          <!-- Checkbox para producto único -->
          <div class="mb-6">
            <label class="flex items-center">
              <input 
                type="checkbox" 
                v-model="product.is_unique" 
                @change="onUniqueProductChange"
                class="mr-2 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              >
              <span class="text-sm font-semibold text-gray-700">
                Producto único (solo una combinación de atributos)
              </span>
            </label>
            <p class="mt-1 text-xs text-gray-500">
              Si está marcado, el producto tendrá solo una combinación de color/talla. 
              Si no, podrás agregar múltiples variantes.
            </p>
          </div>

          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label for="name" class="block mb-2 text-sm font-semibold text-gray-700">Nombre</label>
              <input 
                type="text" 
                v-model="product.name" 
                placeholder="Nombre del producto"
                class="w-full px-4 py-3 mt-1 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                required
              >
            </div>
            <div>
              <label for="price" class="block mb-2 text-sm font-semibold text-gray-700">Precio</label>
              <div class="relative mt-1">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3">
                  <span class="text-sm text-gray-500">$</span>
                </div>
                <input 
                  type="number" 
                  step="0.01" 
                  v-model.number="product.price"
                  placeholder="0.00"
                  class="w-full py-3 pl-8 pr-3 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500" 
                  required
                >
              </div>
            </div>
          </div>


          <!-- Sección de atributos de producto en tres columnas -->
          <div class="mt-6">
            <h3 class="mb-4 text-lg font-semibold text-gray-800">Atributos del Producto</h3>
            <div class="grid items-start grid-cols-1 gap-6 p-6 border-2 border-gray-200 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 md:grid-cols-3">
              <div>
                <label for="genero" class="block mb-2 text-sm font-semibold text-gray-700">Género</label>
                <Combobox v-model="product.genero">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(genero: any) => genero ? genero.charAt(0).toUpperCase() + genero.slice(1) : 'Seleccione el género'"
                        @change="product.genero = $event.target.value"
                        placeholder="Género del producto"
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="genero in ['unisex', 'masculino', 'femenino']"
                        as="template"
                        :key="genero"
                        :value="genero"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <span class="block truncate">
                            {{ genero.charAt(0).toUpperCase() + genero.slice(1) }}
                          </span>
                          <span
                            v-if="selected"
                            :class="[
                              'absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600 ',
                            ]"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              <div>
                <label for="estado" class="block mb-2 text-sm font-semibold text-gray-700">Estado</label>
                <Combobox v-model="product.estado">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(estado: any) => estado ? estado.charAt(0).toUpperCase() + estado.slice(1) : 'Seleccione el estado'"
                        @change="product.estado = $event.target.value"
                        placeholder="Estado del producto"
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="estado in ['nuevo', 'usado']"
                        as="template"
                        :key="estado"
                        :value="estado"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <span
                            :class="[
                              selected ? 'font-medium' : 'font-normal',
                              'block truncate',
                            ]"
                          >
                            {{ estado.charAt(0).toUpperCase() + estado.slice(1) }}
                          </span>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              <div>
                <label for="categoria" class="block mb-2 text-sm font-semibold text-gray-700">Categoría</label>
                <Combobox v-model="product.categoria">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        ref="uniqueCategoryInput"
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(categoria: any) => categoria && categoria !== 'Seleccione la categoría' ? categoria : ''"
                        @change="updateCategorySearch($event.target.value)"
                        @focus="clearCategorySearch($event.target)"
                        placeholder="Buscar categoría..."
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="category in filteredCategories"
                        as="template"
                        :key="category.id"
                        :value="category.name"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <span
                            :class="[
                              selected ? 'font-medium' : 'font-normal',
                              'block truncate',
                            ]"
                          >
                            {{ category.name }}
                          </span>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
            </div>
            <div class="mt-6">
              <label for="description" class="block mb-2 text-sm font-semibold text-gray-700">Descripción</label>
              <textarea 
                v-model="product.description" 
                rows="4"
                placeholder="Describe las características del producto..."
                class="w-full px-4 py-3 mt-1 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm resize-none focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              ></textarea>
            </div>
          </div>

          <div class="mt-6">
            <label class="block text-sm font-medium text-gray-700">Imágenes</label>
            <input type="file" @change="handleFileSelect" multiple
              class="block w-full mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
            
            <!-- Imágenes existentes -->
            <div v-if="existingImages.length > 0" class="mt-4">
              <h4 class="mb-2 text-sm font-medium text-gray-600">Imágenes actuales</h4>
              <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
                <div v-for="(image, index) in existingImages" :key="`existing-${index}`" class="relative">
                  <img :src="image.image_url" class="object-cover w-full h-24 rounded-md" />
                  <button 
                    type="button"
                    @click="removeExistingImage(index)"
                    class="absolute flex items-center justify-center w-6 h-6 text-xs text-white transition-colors bg-red-500 rounded-full -top-2 -right-2 hover:bg-red-600"
                    title="Eliminar imagen"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>

            <!-- Nuevas imágenes seleccionadas -->
            <div v-if="imagePreviews.length > 0" class="mt-4">
              <h4 class="mb-2 text-sm font-medium text-gray-600">Nuevas imágenes seleccionadas</h4>
              <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
                <div v-for="(preview, index) in imagePreviews" :key="`new-${index}`" class="relative">
                  <img :src="preview" class="object-cover w-full h-24 rounded-md" />
                  <button 
                    type="button"
                    @click="removeNewImage(index)"
                    class="absolute flex items-center justify-center w-6 h-6 text-xs text-white transition-colors bg-red-500 rounded-full -top-2 -right-2 hover:bg-red-600"
                    title="Eliminar imagen"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Sección de atributos únicos -->
          <div v-if="product.is_unique" class="mt-6">
            <h3 class="text-lg font-semibold text-gray-800">Atributos del Producto Único</h3>
            <div class="grid items-start grid-cols-1 gap-6 p-6 border-2 border-gray-200 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 md:grid-cols-3">
              <div>
                <label class="block mb-2 text-sm font-semibold text-gray-700">Color</label>
                
                <!-- Combobox personalizado para colores -->
                <Combobox v-model="product.color">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        ref="uniqueColorInput"
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(color: any) => color && color !== 'Seleccione el color' ? color : ''"
                        @change="updateColorSearch($event.target.value)"
                        @focus="clearColorSearch($event.target)"
                        placeholder="Buscar color..."
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="color in filteredColors"
                        as="template"
                        :key="color.id"
                        :value="color.name"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <div class="flex items-center">
                            <!-- Círculo de color -->
                            <div 
                              class="flex-shrink-0 w-4 h-4 mr-3 border border-gray-300 rounded-full"
                              :style="{ backgroundColor: color.hex_code }"
                            ></div>
                            <span
                              :class="[
                                selected ? 'font-medium' : 'font-normal',
                                'block truncate',
                              ]"
                            >
                              {{ color.name }}
                            </span>
                          </div>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              <div>
                <label class="block mb-2 text-sm font-semibold text-gray-700">Talle</label>
                
                <!-- Combobox personalizado para talles -->
                <Combobox v-model="product.talle">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        ref="uniqueSizeInput"
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(talle: any) => talle && talle !== 'Seleccione el talle' ? talle : ''"
                        @change="updateSizeSearch($event.target.value)"
                        @focus="clearSizeSearch($event.target)"
                        placeholder="Buscar talle..."
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="size in filteredSizes"
                        as="template"
                        :key="size.id"
                        :value="size.name"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <span
                            :class="[
                              selected ? 'font-medium' : 'font-normal',
                              'block truncate',
                            ]"
                          >
                            {{ size.name }}
                            <span v-if="size.numeric_size" class="text-gray-500">({{ size.numeric_size }})</span>
                          </span>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              <div>
                <label class="block mb-2 text-sm font-semibold text-gray-700">Stock</label>
                <div class="relative mt-1">
                  <input 
                    type="number" 
                    v-model.number="product.stock" 
                    min="0"
                    step="1"
                    placeholder="Cantidad en stock"
                    class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                    required
                  >
                  <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                    <span class="text-xs text-gray-400">unidades</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sección de variantes múltiples -->
          <div v-else class="mt-6">
            <h3 class="text-lg font-semibold text-gray-800">Variantes</h3>
            <div v-for="(variant, index) in product.variants" :key="index"
              class="grid items-end grid-cols-1 gap-6 p-6 mt-4 border-2 border-gray-200 rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 md:grid-cols-7 ">
              
              <div class="md:col-span-2">
                <label class="block mb-2 text-sm font-semibold text-gray-700">Color</label>
                
                <!-- Combobox personalizado para colores en variantes -->
                <Combobox v-model="variant.color">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(color: any) => color && color !== 'Seleccione el color' ? color : ''"
                        @change="updateVariantColorSearch($event.target.value, index)"
                        @focus="clearVariantColorSearch($event.target, index)"
                        placeholder="Buscar color..."
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="color in filteredColors"
                        as="template"
                        :key="color.id"
                        :value="color.name"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <div class="flex items-center">
                            <!-- Círculo de color -->
                            <div 
                              class="flex-shrink-0 w-4 h-4 mr-3 border border-gray-300 rounded-full"
                              :style="{ backgroundColor: color.hex_code }"
                            ></div>
                            <span
                              :class="[
                                selected ? 'font-medium' : 'font-normal',
                                'block truncate',
                              ]"
                            >
                              {{ color.name }}
                            </span>
                          </div>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              
              <div class="md:col-span-2">
                <label class="block mb-2 text-sm font-semibold text-gray-700">Talle</label>
                
                <!-- Combobox personalizado para talles en variantes -->
                <Combobox v-model="variant.talle">
                  <div class="relative mt-1">
                    <div class="relative w-full overflow-hidden text-left bg-white rounded-lg shadow-md cursor-default focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-teal-300 sm:text-sm">
                      <ComboboxInput
                        class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                        :displayValue="(talle: any) => talle && talle !== 'Seleccione el talle' ? talle : ''"
                        @change="updateVariantSizeSearch($event.target.value, index)"
                        @focus="clearVariantSizeSearch($event.target, index)"
                        placeholder="Buscar talle..."
                      />
                      <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon class="w-5 h-5 text-gray-400" aria-hidden="true" />
                      </ComboboxButton>
                    </div>
                    <ComboboxOptions class="absolute z-10 w-full py-1 mt-1 overflow-auto text-base rounded-md shadow-lg bg-gray-50 max-h-60 ring-1 ring-gray-200 focus:outline-none sm:text-sm">
                      <ComboboxOption
                        v-for="size in filteredSizes"
                        as="template"
                        :key="size.id"
                        :value="size.name"
                        v-slot="{ selected, active }"
                      >
                        <li
                          :class="[
                            active ? 'bg-gray-300' : 'text-gray-900 hover:bg-gray-600 hover:text-white',
                            'relative cursor-default select-none py-2 pl-10 pr-4 transition-colors duration-150',
                          ]"
                        >
                          <span
                            :class="[
                              selected ? 'font-medium' : 'font-normal',
                              'block truncate',
                            ]"
                          >
                            {{ size.name }}
                            <span v-if="size.numeric_size" class="text-gray-500">({{ size.numeric_size }})</span>
                          </span>
                          <span
                            v-if="selected"
                            class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-600"
                          >
                            <CheckIcon class="w-5 h-5" aria-hidden="true" />
                          </span>
                        </li>
                      </ComboboxOption>
                    </ComboboxOptions>
                  </div>
                </Combobox>
              </div>
              
              <div class="md:col-span-2">
                <label class="block mb-2 text-sm font-semibold text-gray-700">Stock</label>
                <div class="relative mt-1">
                  <input 
                    type="number" 
                    v-model.number="variant.stock"
                    min="0"
                    step="1"
                    placeholder="Cantidad en stock"
                    class="w-full py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 transition-all duration-200 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  >
                  <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                    <span class="text-xs text-gray-400">unidades</span>
                  </div>
                </div>
              </div>
              
              <div class="flex items-start justify-start md:col-span-1">
                <button type="button" @click="removeVariant(index)"
                  class="flex items-center px-3 py-2 text-sm font-semibold text-red-600 transition-all duration-200 border-2 border-red-200 rounded-lg bg-red-50 hover:text-red-700 hover:bg-red-100 hover:border-red-300"
                  title="Eliminar variante">
                  <TrashIcon class="w-4 h-4 md:hidden" />
                  <span class="items-center hidden md:flex">
                    <TrashIcon class="w-4 h-4 mr-2" />
                  </span>
                </button>
              </div>
            </div>
            <button type="button" @click="addVariant"
              class="px-6 py-3 mt-6 text-sm font-semibold text-gray-700 transition-all duration-200 border-2 border-gray-300 rounded-lg bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 hover:border-gray-400">
              AÃ±adir Variante
            </button>
          </div>

          <div class="flex justify-end mt-6">
            <button type="button" @click="resetForm"
              class="px-6 py-3 mr-3 text-sm font-semibold text-gray-700 transition-all duration-200 bg-white border-2 border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 hover:border-gray-400">Cancelar</button>
            <button type="submit"
              class="px-6 py-3 text-sm font-semibold text-white transition-all duration-200 transform border border-transparent rounded-lg shadow-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 hover:scale-105">{{
                editing ? 'Actualizar' : 'Guardar' }}</button>
          </div>
        </form>
      </div>

      <!-- Vista previa del producto (4 columnas) -->
      <div class="lg:col-span-4">
        <div class="sticky top-4">
          <div class="p-6 bg-white border rounded-lg shadow-md">
            <h3 class="mb-4 text-lg font-medium text-gray-800">Vista previa del producto</h3>
            <div class="max-w-sm mx-auto">
              <ProductCard :product="previewProduct" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full bg-white border">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Imagen</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Nombre</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Precio</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Pedido</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Tipo</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Stock</th>
            <th class="px-4 py-3 text-xs font-medium tracking-wider text-center text-gray-500 uppercase border-b">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="p in products" :key="p.id" class="hover:bg-gray-50">
            <!-- Imagen miniatura -->
            <td class="px-4 py-3 text-center border-b">
              <div class="flex justify-center">
                <img 
                  :src="p.images && p.images[0] ? p.images[0].image_url : 'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a'" 
                  :alt="p.name"
                  class="object-cover w-12 h-12 rounded-md shadow-sm"
                >
              </div>
            </td>
            <!-- Nombre -->
            <td class="px-4 py-3 text-center border-b">
              <div class="text-sm font-medium text-gray-900">{{ p.name }}</div>
            </td>
            <!-- Precio -->
            <td class="px-4 py-3 text-center border-b">
              <div class="text-sm font-semibold text-gray-900">${{ p.price.toFixed(2) }}</div>
            </td>
            <!-- Pedido -->
            <td class="px-4 py-3 text-center border-b">
              <div class="text-xs text-gray-400">-</div>
            </td>
            <!-- Tipo -->
            <td class="px-4 py-3 text-center border-b">
              <div class="flex justify-center">
                <span :class="p.is_unique ? 'bg-gray-100 text-gray-800' : 'bg-green-100 text-green-800'" 
                      class="inline-flex px-2 py-1 text-xs font-medium rounded-full">
                  {{ p.is_unique ? 'Unico' : 'Variantes' }}
                </span>
              </div>
            </td>
            <!-- Stock -->
            <td class="px-4 py-3 text-center border-b">
              <div class="text-sm font-medium text-gray-900">{{ getProductStock(p) }}</div>
            </td>
            <!-- Acciones -->
            <td class="px-4 py-3 text-center border-b">
              <div class="flex justify-center space-x-2">
                <button 
                  @click="editProduct(p)" 
                  class="p-2 text-indigo-600 transition-colors duration-200 rounded-md hover:text-indigo-900 hover:bg-indigo-50"
                  title="Editar producto"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
                <button 
                  @click="p.id && confirmDelete(p.id)"
                  class="p-2 text-red-600 transition-colors duration-200 rounded-md hover:text-red-900 hover:bg-red-50"
                  title="Eliminar producto"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmationModal :show="showModal" :title="modalTitle" :message="modalMessage" @confirm="handleConfirm"
      @cancel="handleCancel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'vue-toastification';
import { storage } from '../../config/firebase';
import { ref as storageRef, uploadBytes, getDownloadURL } from "firebase/storage";
import imageCompression from 'browser-image-compression';
import { Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption } from '@headlessui/vue';
import { ChevronUpDownIcon, CheckIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/solid';
import ConfirmationModal from '../../components/ui/ConfirmationModal.vue';
import ProductCard from '../../components/products/ProductCard.vue';
import { useAuthStore } from '../../store/auth';
import { useLoading } from '../../composables/useLoading';
import { useProducts } from '../../store/products';
import { masterDataApi, usersApi, config } from '../../config/index';
import type { Color, Category, Size, Product } from '../../types/products/product.types';
import type { Product as GlobalProduct } from '../../types/products/product.types';
import type { AdminProduct, AdminProductVariant, AdminProductImage, AdminProductCreate } from '../../types/products/admin.types';

const toast = useToast();
const authStore = useAuthStore();
const { showLoading, hideLoading } = useLoading();
const { products: storeProducts, fetchProducts: fetchProductsFromStore, addProduct, updateProduct, deleteProduct, invalidateCache } = useProducts();

// === INTERFACES MOVED TO TYPES FOLDER ===

const products = ref<AdminProduct[]>([]);
const editing = ref(false);
const product = ref<AdminProductCreate>({
  name: '',
  description: null,
  price: 0,
  genero: 'unisex',
  estado: 'nuevo',
  categoria: null,
  is_unique: true,
  color: null,
  talle: null,
  stock: 1, // Valor por defecto de 1
  images: [],
  variants: [],
  has_discount: false,
});

const selectedFiles = ref<File[]>([]);
const imagePreviews = ref<string[]>([]);
const existingImages = ref<{ id?: number; image_url: string }[]>([]);
const showModal = ref(false);
const modalTitle = ref('');
const modalMessage = ref('');
const confirmAction = ref<(() => void) | null>(null);

// === DATOS MAESTROS ===
const availableColors = ref<Color[]>([]);
const availableCategories = ref<Category[]>([]);
const availableSizes = ref<Size[]>([]);

// === BÃšSQUEDA EN SELECTS ===
const colorSearchQuery = ref('');
const sizeSearchQuery = ref('');
const categorySearchQuery = ref('');

// === REFS PARA INPUTS ===
// colorInputRefs y sizeInputRefs removidos - no se utilizaban

// === COMPUTED PARA FILTRADO ===
const filteredColors = computed(() => {
  if (!colorSearchQuery.value) return availableColors.value;
  return availableColors.value.filter(color =>
    color.name.toLowerCase().includes(colorSearchQuery.value.toLowerCase())
  );
});

const filteredSizes = computed(() => {
  if (!sizeSearchQuery.value) return availableSizes.value;
  return availableSizes.value.filter(size =>
    size.name.toLowerCase().includes(sizeSearchQuery.value.toLowerCase())
  );
});

const filteredCategories = computed(() => {
  if (!categorySearchQuery.value) return availableCategories.value;
  return availableCategories.value.filter(category =>
    category.name.toLowerCase().includes(categorySearchQuery.value.toLowerCase())
  );
});

// === FUNCIONES DE BÃšSQUEDA ===
const updateColorSearch = (query: string) => {
  colorSearchQuery.value = query;
  // Si encuentra una coincidencia exacta, asignar al producto
  const exactMatch = availableColors.value.find(color => 
    color.name.toLowerCase() === query.toLowerCase()
  );
  if (exactMatch) {
    product.value.color = exactMatch.name;
  }
};

const updateSizeSearch = (query: string) => {
  sizeSearchQuery.value = query;
  // Si encuentra una coincidencia exacta, asignar al producto
  const exactMatch = availableSizes.value.find(size => 
    size.name.toLowerCase() === query.toLowerCase()
  );
  if (exactMatch) {
    product.value.talle = exactMatch.name;
  }
};

const updateVariantColorSearch = (query: string, variantIndex: number) => {
  // Si encuentra una coincidencia exacta, asignar a la variante
  const exactMatch = availableColors.value.find(color => 
    color.name.toLowerCase() === query.toLowerCase()
  );
  if (exactMatch && product.value.variants[variantIndex]) {
    product.value.variants[variantIndex].color = exactMatch.name;
  }
};

const updateVariantSizeSearch = (query: string, variantIndex: number) => {
  // Si encuentra una coincidencia exacta, asignar a la variante
  const exactMatch = availableSizes.value.find(size => 
    size.name.toLowerCase() === query.toLowerCase()
  );
  if (exactMatch && product.value.variants[variantIndex]) {
    product.value.variants[variantIndex].talle = exactMatch.name;
  }
};

const updateCategorySearch = (query: string) => {
  categorySearchQuery.value = query;
  // Si encuentra una coincidencia exacta, asignar al producto
  const exactMatch = availableCategories.value.find(category => 
    category.name.toLowerCase() === query.toLowerCase()
  );
  if (exactMatch) {
    product.value.categoria = exactMatch.name;
  }
};

const clearColorSearch = (inputElement?: HTMLInputElement) => {
  colorSearchQuery.value = '';
  if (inputElement) {
    inputElement.value = '';
    // Limpiar también el modelo si no hay valor seleccionado válido
    if (!product.value.color || product.value.color === 'Seleccione el color') {
      product.value.color = null;
    }
  }
};

const clearSizeSearch = (inputElement?: HTMLInputElement) => {
  sizeSearchQuery.value = '';
  if (inputElement) {
    inputElement.value = '';
    // Limpiar también el modelo si no hay valor seleccionado válido
    if (!product.value.talle || product.value.talle === 'Seleccione el talle') {
      product.value.talle = null;
    }
  }
};

const clearCategorySearch = (inputElement?: HTMLInputElement) => {
  categorySearchQuery.value = '';
  if (inputElement) {
    inputElement.value = '';
    // Limpiar también el modelo si no hay valor seleccionado válido
    if (!product.value.categoria || product.value.categoria === 'Seleccione la categoría') {
      product.value.categoria = null;
    }
  }
};

const clearVariantColorSearch = (inputElement: HTMLInputElement, variantIndex: number) => {
  colorSearchQuery.value = '';
  if (inputElement) {
    inputElement.value = '';
    // Limpiar también el modelo de la variante si no hay valor seleccionado válido
    if (product.value.variants[variantIndex] && 
        (!product.value.variants[variantIndex].color || 
         product.value.variants[variantIndex].color === 'Seleccione el color')) {
      product.value.variants[variantIndex].color = '';
    }
  }
};

const clearVariantSizeSearch = (inputElement: HTMLInputElement, variantIndex: number) => {
  sizeSearchQuery.value = '';
  if (inputElement) {
    inputElement.value = '';
    // Limpiar también el modelo de la variante si no hay valor seleccionado válido
    if (product.value.variants[variantIndex] && 
        (!product.value.variants[variantIndex].talle || 
         product.value.variants[variantIndex].talle === 'Seleccione el talle')) {
      product.value.variants[variantIndex].talle = '';
    }
  }
};

// Vista previa del producto para el ProductCard
const previewProduct = computed((): GlobalProduct => {
  // Combinar imágenes existentes y nuevas para el preview
  const allImages: { id: number; image_url: string; is_primary: boolean }[] = [];
  
  // Agregar imágenes existentes
  if (existingImages.value.length > 0) {
    allImages.push(...existingImages.value.map((img, index) => ({ 
      id: index, 
      image_url: img.image_url,
      is_primary: index === 0 // Marcar la primera imagen como principal
    })));
  }
  
  // Agregar nuevas imágenes seleccionadas
  if (imagePreviews.value.length > 0) {
    allImages.push(...imagePreviews.value.map((url, index) => ({
      id: existingImages.value.length + index, 
      image_url: url,
      is_primary: allImages.length === 0 && index === 0 // Marcar como principal si es la primera
    })));
  }
  
  // Si no hay imágenes, usar imagen por defecto
  if (allImages.length === 0) {
    allImages.push({ 
      id: 0, 
      image_url: 'https://firebasestorage.googleapis.com/v0/b/m-vintage.firebasestorage.app/o/modelo_card.jpg?alt=media&token=bfeea622-2abf-4d84-b570-96659c605f8a',
      is_primary: true
    });
  }

  // Precio del producto
  const price = Number(product.value.price) || 0;

  // Crear variantes para la vista previa
  const previewVariants = product.value.is_unique 
    ? [] 
    : product.value.variants.map((v, index) => ({
        id: index,
        color_id: 0, // Placeholder ID
        size_id: 0, // Placeholder ID
        image_url: '',
        size: v.talle || '',
        stock: v.stock || 0,
        color: v.color || ''
      }));

  // Crear objeto de producto para la vista previa
  const previewData: GlobalProduct = {
    id: 1, // ID temporal para la vista previa
    name: product.value.name || 'Nombre del producto',
    description: product.value.description || 'Descripción del producto',
    price: price,
    genero: product.value.genero || 'unisex',
    estado: product.value.estado || 'nuevo',
    categoria: product.value.categoria || undefined,
    is_unique: product.value.is_unique || false,
    color: product.value.color || null,
    talle: product.value.talle || null,
    stock: product.value.stock || 0,
    has_discount: false,
    discount_percentage: null,
    discounted_price: undefined,
    discount_amount: 0,
    images: allImages,
    variants: previewVariants,
    // Propiedades opcionales con valores por defecto
    is_new: false,
    is_sale: false,
    original_price: price
  };

  return previewData;
});

// === LÃ“GICA DE DATOS MAESTROS ===
async function loadMasterData() {
  try {
    // Cargar colores, categorías y talles usando la nueva API
    const colors = await masterDataApi.getColors();
    const categories = await masterDataApi.getCategories();
    const sizes = await masterDataApi.getSizes();

    availableColors.value = colors;
    availableCategories.value = categories;
    availableSizes.value = sizes;
    
  } catch (error) {
    toast.error('Error cargando datos de colores, categorías y talles');
  }
}

// --- Lógica de la API ---
async function fetchProducts() {
  if (import.meta.env.VITEST) return;

  if (!authStore.token) {
    return;
  }

  // Debug: verificar estado de autenticación
  try {
    const debugResponse = await usersApi.getUserDebugInfo();

    const hasPermissions = debugResponse.has_admin_role || debugResponse.has_manager_role;

    if (!hasPermissions) {
      toast.error('No tienes permisos para gestionar productos. Contacta al administrador.');
      return;
    }
  } catch (debugError) {
  }

  try {
    // Usar el store para obtener productos
    const fetchedProducts = await fetchProductsFromStore();
    // Convertir Product[] a AdminProduct[] para compatibilidad temporal
    products.value = fetchedProducts as any[];
  } catch (error) {
    toast.error('Error al cargar productos. Verifica que el backend estÃ© funcionando.');
  }
}

async function saveProduct() {
  showLoading(
    editing.value ? 'Actualizando producto...' : 'Agregando producto...',
    'Por favor espera mientras procesamos tu solicitud'
  );

  if (!authStore.token) {
    toast.error('No estás autenticado. Por favor inicia sesin.');
    hideLoading();
    return;
  }

  // Debug: verificar permisos antes de guardar
  try {
    const debugResponse = await usersApi.getUserDebugInfo();

    const hasPermissions = debugResponse.has_admin_role || debugResponse.has_manager_role;
    
    if (!hasPermissions) {
      toast.error('No tienes permisos para gestionar productos. Tu cuenta necesita rol de Admin o Manager.');
      hideLoading();
      return;
    }
  } catch (debugError) {
    toast.error('Error verificando permisos. Verifica tu autenticación.');
    hideLoading();
    return;
  }

  // Validar datos del producto
  if (product.value.is_unique) {
    if (!product.value.color && !product.value.talle) {
      toast.error('Los productos únicos deben tener al menos color o talla especificado');
      hideLoading();
      return;
    }
    if (product.value.stock === null || product.value.stock === undefined || product.value.stock < 0) {
      toast.error('Los productos únicos deben tener stock especificado');
      hideLoading();
      return;
    }
  } else {
    if (product.value.variants.length === 0) {
      toast.error('Los productos con variantes deben tener al menos una variante');
      hideLoading();
      return;
    }
    // Validar que todas las variantes tengan datos válidos
    for (const variant of product.value.variants) {
      if (variant.stock < 0) {
        toast.error('Todas las variantes deben tener stock válido');
        hideLoading();
        return;
      }
    }
  }


  try {
    // Preparar array de imágenes final
    let finalImageUrls: string[] = [];
    
    // Agregar imágenes existentes que no fueron eliminadas
    finalImageUrls.push(...existingImages.value.map(img => img.image_url));
    
    // Subir nuevas imágenes a Firebase Storage si hay archivos seleccionados
    if (selectedFiles.value.length > 0) {
      const newImageUrls = await uploadImages();
      finalImageUrls.push(...newImageUrls);
    }
    
    // Asignar todas las imágenes al producto
    product.value.images = finalImageUrls;

    const editingProduct = editing.value ? products.value.find(p => p.name === product.value.name) : null;

    // Preparar request para enviar al backend

    let savedProduct;
    if (editing.value && editingProduct?.id) {
      // Usar store para actualizar producto
      savedProduct = await updateProduct(editingProduct.id, product.value as any);
    } else {
      // Usar store para crear producto
      savedProduct = await addProduct(product.value as any);
    }

    // El store ya actualiza automáticamente la cache
    products.value = storeProducts.value as any[];
    resetForm();
    toast.success(` Producto ${editing.value ? 'actualizado' : 'creado'} exitosamente!`);
  } catch (error) {
    toast.error(`Error al ${editing.value ? 'actualizar' : 'crear'} producto: ${error instanceof Error ? error.message : 'Error desconocido'}`);
  } finally {
    hideLoading();
  }
}

async function deleteProductById(id?: number) {
  if (!id) return;

  if (!authStore.token) {
    toast.error('No estás autenticado. Por favor inicia sesión.');
    return;
  }

  try {
    // Usar store para eliminar producto
    await deleteProduct(id);
    // El store ya actualiza automáticamente la cache
    products.value = storeProducts.value as any[];
    toast.success('Producto eliminado exitosamente!');
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'Error al eliminar producto';
    toast.error(`${errorMessage}`);
  }
}// --- Lógica de Imágenes ---
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    // Filtrar solo imagenes soportadas
    const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const validFiles = Array.from(target.files).filter(file => 
      supportedTypes.includes(file.type)
    );
    
    if (validFiles.length !== target.files.length) {
      toast.warning(`Se ignoraron ${target.files.length - validFiles.length} archivos no soportados`);
    }
    
    selectedFiles.value = validFiles;
    imagePreviews.value = [];
    for (const file of selectedFiles.value) {
      imagePreviews.value.push(URL.createObjectURL(file));
    }
  }
}

// Función para eliminar imagen existente
function removeExistingImage(index: number) {
  existingImages.value.splice(index, 1);
  toast.info('Imagen existente marcada para eliminación');
}

// Función para eliminar nueva imagen seleccionada
function removeNewImage(index: number) {
  // Liberar memoria del objeto URL
  URL.revokeObjectURL(imagePreviews.value[index]);
  
  // Eliminar de ambos arrays
  imagePreviews.value.splice(index, 1);
  selectedFiles.value.splice(index, 1);
  
  toast.info('Nueva imagen eliminada del preview');
}

async function compressToWebP(file: File): Promise<File> {
  const options = {
    maxSizeMB: 1,                    // Maximo 1MB
    useWebWorker: true,              // Usar Web Worker para no bloquear UI
    fileType: 'image/webp',          // Convertir a WebP
    initialQuality: 0.85,            // Calidad inicial 85%
    maxWidthOrHeight: 1920,          // Redimensionar si es muy grande
  };

  try {
    const compressedFile = await imageCompression(file, options);
    return compressedFile;
  } catch (error) {
    throw error;
  }
}

async function uploadImages(): Promise<string[]> {

  try {
    const uploadPromises = selectedFiles.value.map(async (file, index) => {
      // NUEVO: Comprimir y convertir a WebP
      const compressedFile = await compressToWebP(file);
      
      // Generar nombre con extensin .webp
      const originalName = file.name.replace(/\.[^/.]+$/, ''); // Remover extensin original
      const fileName = `${Date.now()}_${originalName}.webp`;
      const fileRef = storageRef(storage, `products/${fileName}`);

      const snapshot = await uploadBytes(fileRef, compressedFile);
      const downloadURL = await getDownloadURL(snapshot.ref);

      return downloadURL;
    });

    const imageUrls = await Promise.all(uploadPromises);
    return imageUrls;
  } catch (error) {
    throw new Error(`Error al subir imágenes: ${error instanceof Error ? error.message : 'Error desconocido'}`);
  }
}

// --- Lógica del Formulario ---
function editProduct(p: any) {
  editing.value = true;
  product.value = {
    name: p.name,
    description: p.description,
    price: p.price,
    genero: p.genero,
    estado: p.estado,
    categoria: p.categoria || null,
    is_unique: p.is_unique,
    color: p.color || null,
    talle: p.talle || null,
    stock: p.stock || null,
    images: p.images.map((img: any) => img.image_url),
    variants: p.variants?.map((v: any) => ({ color: v.color || v.size, talle: v.talle || v.size, stock: v.stock })) || [],
    has_discount: p.has_discount || false
  };
  
  // Separar imágenes existentes de nuevas imágenes
  existingImages.value = p.images.map((img: any) => ({ 
    id: img.id, 
    image_url: img.image_url 
  }));
  
  // Limpiar arrays de nuevas imágenes
  imagePreviews.value = [];
  selectedFiles.value = [];
}

function addVariant() {
  if (!product.value.is_unique) {
    product.value.variants.push({ color: '', talle: '', stock: 1 }); // Stock por defecto 1
  }
}

function removeVariant(index: number) {
  if (!product.value.is_unique) {
    product.value.variants.splice(index, 1);
  }
}

function onUniqueProductChange() {
  if (product.value.is_unique) {
    // Si cambia a único, limpiar variantes y mover la primera variante (si existe) a los campos únicos
    if (product.value.variants.length > 0) {
      const firstVariant = product.value.variants[0];
      product.value.color = firstVariant.color;
      product.value.talle = firstVariant.talle;
      product.value.stock = firstVariant.stock;
    } else {
      // Si no hay variantes, poner stock por defecto a 1
      product.value.stock = 1;
    }
    product.value.variants = [];
  } else {
    // Si cambia a variantes, mover los campos únicos a una nueva variante
    if (product.value.color || product.value.talle || product.value.stock) {
      product.value.variants = [{
        color: product.value.color || null,
        talle: product.value.talle || null,
        stock: product.value.stock || 1
      }];
    } else {
      // Si no hay datos únicos, crear una variante vacía con stock 1
      product.value.variants = [{ color: '', talle: '', stock: 1 }];
    }
    product.value.color = null;
    product.value.talle = null;
    product.value.stock = null;
  }
}

function getProductStock(p: any): number {
  if (p.is_unique) {
    return p.stock || 0;
  } else {
    return p.variants.reduce((total: number, variant: any) => total + variant.stock, 0);
  }
}

function resetForm() {
  editing.value = false;
  product.value = { 
    name: '', 
    description: null, 
    price: 0, 
    genero: 'unisex', 
    estado: 'nuevo',
    categoria: null,
    is_unique: true,
    color: null,
    talle: null,
    stock: 1, // Stock por defecto 1
    images: [], 
    variants: [],
    has_discount: false
  };
  
  // Limpiar URLs de objeto para liberar memoria antes de limpiar arrays
  imagePreviews.value.forEach(url => {
    try {
      URL.revokeObjectURL(url);
    } catch (error) {
      // Ignorar errores al liberar URLs
    }
  });
  
  // Limpiar arrays de imágenes
  selectedFiles.value = [];
  imagePreviews.value = [];
  existingImages.value = [];
}


// --- Lógica del Modal ---
function confirmSave() {
  modalTitle.value = editing.value ? 'Confirmar Actualización' : 'Confirmar Creación';
  modalMessage.value = `¿Estás seguro de que deseas ${editing.value ? 'actualizar' : 'guardar'} este producto?`;
  confirmAction.value = saveProduct;
  showModal.value = true;
}

function confirmDelete(id: number) {
  modalTitle.value = 'Confirmar Eliminación';
  modalMessage.value = '¿Estás seguro de que deseas eliminar este producto?';
  confirmAction.value = () => deleteProductById(id);
  showModal.value = true;
}

function handleConfirm() {
  if (confirmAction.value) {
    confirmAction.value();
  }
  showModal.value = false;
}

function handleCancel() {
  showModal.value = false;
}

onMounted(async () => {
  await loadMasterData();
  await fetchProducts();
});

</script>

