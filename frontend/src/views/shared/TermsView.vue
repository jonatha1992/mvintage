<template>
  <div class="min-h-screen bg-white py-16">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-light tracking-wide text-gray-900 mb-4">Términos y Condiciones</h1>
        <p class="text-lg text-gray-600">Última actualización: {{ lastUpdated }}</p>
      </div>

      <div class="prose prose-lg max-w-none">
        <div class="space-y-8">
          <!-- 1. Aceptación de términos -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">1. Aceptación de los Términos</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Al acceder y utilizar el sitio web de Showroom Isabella (el "Sitio"), usted acepta estar sujeto a estos
              Términos y Condiciones de uso. Si no está de acuerdo con alguna parte de estos términos, 
              no debe utilizar nuestro sitio web.
            </p>
            <p class="text-gray-700 leading-relaxed">
              Estos términos se aplican a todos los visitantes, usuarios y otras personas que accedan 
              o utilicen el servicio.
            </p>
          </section>

          <!-- 2. Descripción del servicio -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">2. Descripción del Servicio</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Showroom Isabella es una tienda online de ropa vintage y contemporánea. Ofrecemos una plataforma
              para la compra de productos de moda, accesorios y artículos relacionados.
            </p>
            <p class="text-gray-700 leading-relaxed">
              Nos reservamos el derecho de modificar, suspender o discontinuar cualquier aspecto del 
              servicio en cualquier momento sin previo aviso.
            </p>
          </section>

          <!-- 3. Registro y cuenta -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">3. Registro y Cuenta de Usuario</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Para realizar compras, es necesario crear una cuenta proporcionando información precisa y completa. 
              Usted es responsable de mantener la confidencialidad de su cuenta y contraseña.
            </p>
            <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
              <li>Debe ser mayor de 18 años para crear una cuenta</li>
              <li>La información proporcionada debe ser veraz y actualizada</li>
              <li>Es responsable de todas las actividades que ocurran bajo su cuenta</li>
              <li>Debe notificarnos inmediatamente sobre cualquier uso no autorizado</li>
            </ul>
          </section>

          <!-- 4. Productos y precios -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">4. Productos y Precios</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Nos esforzamos por mostrar con precisión los colores y detalles de nuestros productos. 
              Sin embargo, no podemos garantizar que la visualización en su dispositivo sea exacta.
            </p>
            <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
              <li>Los precios están sujetos a cambios sin previo aviso</li>
              <li>Los precios incluyen impuestos aplicables</li>
              <li>Nos reservamos el derecho de limitar cantidades</li>
              <li>Los productos están sujetos a disponibilidad</li>
            </ul>
          </section>

          <!-- 5. Proceso de compra -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">5. Proceso de Compra y Pago</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Al realizar un pedido, está haciendo una oferta para comprar el producto. Todas las órdenes 
              están sujetas a aceptación y confirmación del precio del producto.
            </p>
            <div class="bg-gray-50 p-4 rounded-lg mb-4">
              <h3 class="font-medium text-gray-900 mb-2">Métodos de Pago Aceptados:</h3>
              <ul class="list-disc list-inside text-gray-700 space-y-1">
                <li>Mercado Pago (tarjetas de crédito y débito)</li>
                <li>Transferencia bancaria</li>
              </ul>
            </div>
          </section>

          <!-- 6. Retiro -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">6. Retiro en el local</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Todas las compras se retiran en el local, sin costo adicional. Te avisamos por WhatsApp cuando tu pedido esté listo para retirar.
            </p>
            <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
              <li>Modalidad exclusiva de retiro en el local</li>
              <li>El retiro se coordina previamente por WhatsApp</li>
              <li>Se debe presentar el número de pedido</li>
            </ul>
          </section>

          <!-- 7. Devoluciones y cambios -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">7. Devoluciones y Cambios</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Aceptamos devoluciones dentro de los 30 días posteriores a la recepción del producto, 
              siempre que el artículo esté en condiciones originales.
            </p>
            <div class="bg-blue-50 p-4 rounded-lg mb-4">
              <h3 class="font-medium text-gray-900 mb-2">Condiciones para Devoluciones:</h3>
              <ul class="list-disc list-inside text-gray-700 space-y-1">
                <li>El producto debe estar sin usar y con etiquetas originales</li>
                <li>Debe incluir el comprobante de compra</li>
                <li>La devolución se coordina en el showroom</li>
                <li>El reembolso se procesará dentro de 5-10 días hábiles</li>
              </ul>
            </div>
          </section>

          <!-- 8. Propiedad intelectual -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">8. Propiedad Intelectual</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Todo el contenido del sitio web, incluyendo textos, gráficos, logos, íconos, imágenes, 
              clips de audio y software, es propiedad de Showroom Isabella y está protegido por las leyes
              de derechos de autor.
            </p>
            <p class="text-gray-700 leading-relaxed">
              No está permitido reproducir, distribuir, modificar o crear trabajos derivados del 
              contenido sin autorización expresa por escrito.
            </p>
          </section>

          <!-- 9. Limitación de responsabilidad -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">9. Limitación de Responsabilidad</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              En ningún caso Showroom Isabella será responsable por daños indirectos, incidentales, especiales
              o consecuentes que resulten del uso o la imposibilidad de usar el sitio web o los productos.
            </p>
            <p class="text-gray-700 leading-relaxed">
              Nuestra responsabilidad total no excederá el monto pagado por el producto específico 
              que dio origen al reclamo.
            </p>
          </section>

          <!-- 10. Privacidad -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">10. Privacidad y Protección de Datos</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Respetamos su privacidad y estamos comprometidos con la protección de sus datos personales. 
              Para más información, consulte nuestra 
              <router-link to="/privacy" class="text-blue-600 hover:text-blue-800 underline">
                Política de Privacidad
              </router-link>.
            </p>
          </section>

          <!-- 11. Modificaciones -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">11. Modificaciones de los Términos</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Nos reservamos el derecho de modificar estos términos en cualquier momento. 
              Las modificaciones entrarán en vigor inmediatamente después de su publicación en el sitio web.
            </p>
            <p class="text-gray-700 leading-relaxed">
              Es su responsabilidad revisar periódicamente estos términos para estar al tanto de las actualizaciones.
            </p>
          </section>

          <!-- 12. Ley aplicable -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">12. Ley Aplicable y Jurisdicción</h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              Estos términos se rigen por las leyes de la República Argentina. Cualquier disputa 
              será resuelta en los tribunales competentes de la Ciudad Autónoma de Buenos Aires.
            </p>
          </section>

          <!-- 13. Contacto -->
          <section>
            <h2 class="text-2xl font-light text-gray-900 mb-4">13. Información de Contacto</h2>
            <div class="bg-gray-50 p-6 rounded-lg">
              <p class="text-gray-700 mb-4">
                Si tiene preguntas sobre estos Términos y Condiciones, puede contactarnos:
              </p>
              <div class="space-y-2 text-gray-700">
                <p><strong>Email:</strong> 
                  <a href="mailto:Showroomisabellaa@gmail.com" class="text-blue-600 hover:text-blue-800">
                    Showroomisabellaa@gmail.com
                  </a>
                </p>
                <p><strong>Teléfono:</strong> 
                  <a href="tel:+5491176372876" class="text-blue-600 hover:text-blue-800">
                    +54 9 11 7637-2876
                  </a>
                </p>
                <p><strong>Dirección:</strong> Buenos Aires, Argentina</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const lastUpdated = computed(() => {
  return new Date().toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})
</script>
