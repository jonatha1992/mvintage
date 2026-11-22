<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" v-reveal="0">
        <h1 class="text-3xl font-bold text-gray-900 font-heading">Guía de talles</h1>
        <p class="text-gray-600 mt-2 font-body">Encontrá tu talle ideal</p>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="bg-white rounded-lg shadow-sm p-6 sm:p-8" v-reveal="1">
        <!-- Cómo medirte -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-3 font-heading">Cómo medirte</h2>
          <p class="text-gray-600 font-body">
            Para tomarte las medidas de forma precisa, usá un centímetro de costura sobre ropa al cuerpo y sin ajustar.
          </p>
        </div>

        <div class="space-y-10">
          <!-- Prendas superiores -->
          <div>
            <h3 class="text-xl font-semibold text-gray-900 mb-4 font-heading">
              Prendas superiores (tops, blusas, remeras, bodys, vestidos)
            </h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-left font-body text-sm">
                <thead>
                  <tr class="border-b text-gray-900">
                    <th class="py-2 px-3 font-semibold">Talle</th>
                    <th class="py-2 px-3 font-semibold">Busto (cm)</th>
                    <th class="py-2 px-3 font-semibold">Cintura (cm)</th>
                    <th class="py-2 px-3 font-semibold">Cadera (cm)</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-gray-700">
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">XS</td>
                    <td class="py-2 px-3">82-86</td>
                    <td class="py-2 px-3">62-66</td>
                    <td class="py-2 px-3">87-91</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">S</td>
                    <td class="py-2 px-3">87-91</td>
                    <td class="py-2 px-3">67-71</td>
                    <td class="py-2 px-3">92-96</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">M</td>
                    <td class="py-2 px-3">92-96</td>
                    <td class="py-2 px-3">72-76</td>
                    <td class="py-2 px-3">97-101</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">L</td>
                    <td class="py-2 px-3">97-102</td>
                    <td class="py-2 px-3">77-82</td>
                    <td class="py-2 px-3">102-107</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">XL</td>
                    <td class="py-2 px-3">103-108</td>
                    <td class="py-2 px-3">83-88</td>
                    <td class="py-2 px-3">108-113</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Pantalones y jeans -->
          <div>
            <h3 class="text-xl font-semibold text-gray-900 mb-4 font-heading">
              Pantalones y jeans
            </h3>
            <div class="overflow-x-auto">
              <table class="min-w-full text-left font-body text-sm">
                <thead>
                  <tr class="border-b text-gray-900">
                    <th class="py-2 px-3 font-semibold">Talle (AR)</th>
                    <th class="py-2 px-3 font-semibold">Equivalencia</th>
                    <th class="py-2 px-3 font-semibold">Cintura (cm)</th>
                    <th class="py-2 px-3 font-semibold">Cadera (cm)</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-gray-700">
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">36</td>
                    <td class="py-2 px-3">XS</td>
                    <td class="py-2 px-3">64-68</td>
                    <td class="py-2 px-3">90-94</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">38</td>
                    <td class="py-2 px-3">S</td>
                    <td class="py-2 px-3">68-72</td>
                    <td class="py-2 px-3">94-98</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">40</td>
                    <td class="py-2 px-3">M</td>
                    <td class="py-2 px-3">72-76</td>
                    <td class="py-2 px-3">98-102</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">42</td>
                    <td class="py-2 px-3">L</td>
                    <td class="py-2 px-3">76-80</td>
                    <td class="py-2 px-3">102-106</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-2 px-3 font-medium text-gray-900">44</td>
                    <td class="py-2 px-3">XL</td>
                    <td class="py-2 px-3">80-84</td>
                    <td class="py-2 px-3">106-110</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Consejos de medición -->
        <div class="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 class="text-lg font-semibold text-gray-900 mb-3 font-heading">Consejos para medirte</h3>
          <ul class="space-y-2 text-gray-600 font-body">
            <li>• <strong>Busto:</strong> Medí alrededor de la parte más prominente del busto.</li>
            <li>• <strong>Cintura:</strong> Medí alrededor de la parte más estrecha de la cintura.</li>
            <li>• <strong>Cadera:</strong> Medí alrededor de la parte más ancha de la cadera.</li>
            <li>• <strong>Largo:</strong> Medí desde el hombro hasta el largo deseado.</li>
          </ul>
          <p class="mt-4 text-sm text-gray-500 italic font-body">
            Las medidas son orientativas y pueden variar según la prenda.
          </p>
        </div>

        <!-- Contacto -->
        <div class="mt-8 text-center font-body">
          <p class="text-gray-600">
            ¿Tenés dudas con tu talle? <a
              href="https://wa.me/5491176372876?text=Hola!%20Tengo%20una%20consulta%20sobre%20talles"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-600 hover:underline font-medium"
            >Escribinos por WhatsApp</a> o por correo a
            <a href="mailto:Showroomisabellaa@gmail.com" class="text-blue-600 hover:underline font-medium">Showroomisabellaa@gmail.com</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { vReveal } from '../../composables/useReveal'
</script>