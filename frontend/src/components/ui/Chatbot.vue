<template>
  <div class="chatbot-container">
    <!-- Botón flotante del chatbot -->
    <button @click="toggleChat"
      class="fixed z-50 flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 text-black transition-all duration-300 bg-white border border-black rounded-full shadow-lg hover:bg-gray-100"
      style="right: max(1rem, env(safe-area-inset-right, 0px)); bottom: max(1rem, env(safe-area-inset-bottom, 0px));"
      :class="{ 'rotate-45': isChatOpen }">
      <img v-if="!isChatOpen" src="/logo_redondo.jpg" alt="Chat de Showroom Isabella" class="object-cover w-12 h-12 sm:w-14 sm:h-14 rounded-full" />
      <svg v-else class="w-6 h-6" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>

    <!-- Ventana del chat -->
    <div v-if="isChatOpen"
      class="fixed z-40 flex flex-col bg-white border border-gray-200 rounded-lg shadow-xl w-[min(20rem,calc(100vw-2rem))] h-96"
      style="right: max(1rem, env(safe-area-inset-right, 0px)); bottom: calc(5.5rem + env(safe-area-inset-bottom, 0px));">
      <!-- Header del chat -->
      <div class="flex items-center p-4 space-x-3 text-white bg-black rounded-t-lg">
        <img src="/logo_redondo.jpg" alt="Showroom Isabella" class="object-cover w-8 h-8 rounded-full" />
        <div>
          <h3 class="font-heading font-medium">Asistente de Showroom Isabella</h3>
          <p class="font-body text-xs text-body-text">¿En qué puedo ayudarte?</p>
        </div>
      </div>

      <!-- Área de mensajes -->
      <div ref="messagesContainer" class="flex-1 p-4 space-y-3 overflow-y-auto bg-gray-50">
        <div v-for="message in messages" :key="message.id" class="flex"
          :class="message.isUser ? 'justify-end' : 'justify-start'">
          <div class="max-w-xs px-4 py-2 rounded-lg" :class="message.isUser
            ? 'bg-black text-white'
            : 'bg-white text-gray-900 border border-gray-200'">
            <p class="font-body text-sm">{{ message.text }}</p>
            <button v-if="message.action === 'whatsapp' && message.whatsappMessage"
              @click="openWhatsApp(message.whatsappMessage)"
              class="flex items-center px-3 py-1 mt-2 space-x-1 text-xs text-white transition-colors bg-green-500 rounded-full hover:bg-green-600">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path
                  d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.51 3.487" />
              </svg>
              <span class="font-body">Abrir WhatsApp</span>
            </button>
            <span class="font-body block mt-1 text-xs opacity-70">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>

        <!-- Indicador de escritura -->
        <div v-if="isTyping" class="flex justify-start">
          <div class="px-4 py-2 text-gray-900 bg-white border border-gray-200 rounded-lg">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input de mensaje -->
      <div class="p-4 bg-white border-t border-gray-200 rounded-b-lg">
        <div class="flex space-x-2">
          <input v-model="newMessage" @keypress.enter="sendMessage" @input="handleTyping"
            placeholder="Escribe tu mensaje..."
            class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent" />
          <button @click="sendMessage" :disabled="!newMessage.trim()"
            class="px-4 py-2 text-white transition-colors bg-black rounded-md hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Sugerencias rápidas -->
      <div v-if="showSuggestions" class="p-3 bg-gray-100 border-t border-gray-200">
        <p class="font-body mb-2 text-xs text-body-text">Preguntas frecuentes:</p>
        <div class="flex flex-wrap gap-1">
          <button v-for="suggestion in quickSuggestions" :key="suggestion" @click="sendQuickMessage(suggestion)"
            class="px-2 py-1 text-xs transition-colors bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            <span class="font-body">{{ suggestion }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';

interface ChatMessage {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  action?: 'whatsapp';
  whatsappMessage?: string;
}

const isChatOpen = ref(false);
const newMessage = ref('');
const isTyping = ref(false);
const showSuggestions = ref(true);
const messagesContainer = ref<HTMLElement>();
const messages = ref<ChatMessage[]>([]);

const quickSuggestions = [
  '¿Cómo retiro mi pedido?',
  'Tallas disponibles',
  'Política de devolución',
  'Métodos de pago',
  'Contacto'
];

// Número de WhatsApp de Showroom Isabella
const WHATSAPP_NUMBER = '5491176372876';

// Función para crear enlace de WhatsApp
const createWhatsAppLink = (message: string) => {
  const encodedMessage = encodeURIComponent(message);
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodedMessage}`;
};

// Respuestas predefinidas del bot que redirigen a WhatsApp
const botResponses: { [key: string]: { text: string; action?: 'whatsapp'; whatsappMessage?: string } } = {
  'hola': { text: '¡Hola! Bienvenido a Showroom Isabella. Para una atención personalizada, te conectamos con nuestro equipo vía WhatsApp.' },
  'retiro': {
    text: 'Todas las compras se retiran sin costo en Alonso Pareja 6542, González Catán (Buenos Aires). Coordiná día y horario por WhatsApp.',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría consultar cómo coordinar el retiro de mi pedido.'
  },
  'tallas disponibles': {
    text: 'Para verificar tallas disponibles de productos específicos, consulta con nuestro equipo via WhatsApp 👕',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría consultar sobre tallas disponibles de productos.'
  },
  'política de devolución': {
    text: 'Realizamos cambios dentro de los 7 días hábiles posteriores al retiro. Para coordinarlo, escribinos por WhatsApp.',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría consultar por un cambio.'
  },
  'métodos de pago': {
    text: 'Para conocer todos nuestros métodos de pago disponibles, consulta via WhatsApp 💳',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría conocer los métodos de pago disponibles.'
  },
  'contacto': {
    text: 'Te conectamos directamente con nuestro equipo de atención al cliente via WhatsApp 📞',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría contactarme con el equipo de Showroom Isabella.'
  },
  'envios': {
    text: 'Las compras se retiran en el showroom. Podemos ayudarte a coordinar por WhatsApp.',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría consultar cómo coordinar el retiro de mi compra.'
  },
  'tienda': { text: 'Somos Showroom Isabella. Para conocer más, contactanos por WhatsApp.' },
  'productos': {
    text: 'Para consultar sobre productos específicos y disponibilidad, nuestro equipo te ayudará via WhatsApp 👗',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Me gustaría consultar sobre productos disponibles.'
  },
  'ayuda': {
    text: 'Nuestro equipo está listo para ayudarte con cualquier consulta via WhatsApp 🤝',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Necesito ayuda con una consulta sobre Showroom Isabella.'
  }
};

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value;

  if (isChatOpen.value && messages.value.length === 0) {
    // Mensaje de bienvenida
    setTimeout(() => {
      addBotMessage({ text: '¡Hola! Soy el asistente virtual de Showroom Isabella. ¿En qué puedo ayudarte hoy?' });
    }, 500);
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim()) return;

  const userMessage = newMessage.value.trim();
  addUserMessage(userMessage);
  newMessage.value = '';
  showSuggestions.value = false;

  // Simular que el bot está escribiendo
  isTyping.value = true;

  setTimeout(() => {
    isTyping.value = false;
    const response = getBotResponse(userMessage);
    addBotMessage(response);
  }, 1000 + Math.random() * 1000); // Tiempo aleatorio entre 1-2 segundos
};

const sendQuickMessage = (suggestion: string) => {
  // Mapear sugerencias a mensajes de WhatsApp específicos
  const whatsappMessages: { [key: string]: string } = {
    '¿Cómo retiro mi pedido?': 'Hola! Me gustaría consultar cómo coordinar el retiro de mi pedido.',
    'Tallas disponibles': 'Hola! Me gustaría consultar sobre tallas disponibles de productos.',
    'Política de devolución': 'Hola! Me gustaría conocer más sobre la política de devoluciones.',
    'Métodos de pago': 'Hola! Me gustaría conocer los métodos de pago disponibles.',
    'Contacto': 'Hola! Me gustaría contactarme con el equipo de Showroom Isabella.'
  };

  const whatsappMessage = whatsappMessages[suggestion] || `Hola! Tengo una consulta sobre: ${suggestion}`;
  openWhatsApp(whatsappMessage);
};

const addUserMessage = (text: string) => {
  messages.value.push({
    id: Date.now(),
    text,
    isUser: true,
    timestamp: new Date()
  });
  scrollToBottom();
};

const addBotMessage = (response: { text: string; action?: 'whatsapp'; whatsappMessage?: string }) => {
  messages.value.push({
    id: Date.now(),
    text: response.text,
    isUser: false,
    timestamp: new Date(),
    action: response.action,
    whatsappMessage: response.whatsappMessage
  });
  scrollToBottom();
};

const getBotResponse = (userMessage: string): { text: string; action?: 'whatsapp'; whatsappMessage?: string } => {
  const lowerMessage = userMessage.toLowerCase();

  // Buscar palabras clave en el mensaje
  for (const [key, response] of Object.entries(botResponses)) {
    if (lowerMessage.includes(key)) {
      return response;
    }
  }

  // Respuestas por categorías más amplias
  if (lowerMessage.includes('precio') || lowerMessage.includes('costo') || lowerMessage.includes('cuanto')) {
    return {
      text: 'Para consultar precios específicos y ofertas disponibles, nuestro equipo te ayudará via WhatsApp 💰',
      action: 'whatsapp',
      whatsappMessage: 'Hola! Me gustaría consultar sobre precios de productos.'
    };
  }

  if (lowerMessage.includes('stock') || lowerMessage.includes('disponible')) {
    return {
      text: 'Para verificar stock en tiempo real, consulta con nuestro equipo via WhatsApp 📦',
      action: 'whatsapp',
      whatsappMessage: 'Hola! Me gustaría consultar sobre stock de productos.'
    };
  }

  if (lowerMessage.includes('gracias')) {
    return { text: '¡De nada! Si necesitas más ayuda, contactanos via WhatsApp. ¡Estamos aquí para ti! 😊' };
  }

  // Respuesta por defecto
  return {
    text: 'Para obtener información personalizada y específica, nuestro equipo te atenderá via WhatsApp 📱',
    action: 'whatsapp',
    whatsappMessage: 'Hola! Tengo una consulta sobre Showroom Isabella.'
  };
};

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const handleTyping = () => {
  showSuggestions.value = false;
};

const openWhatsApp = (message?: string) => {
  const whatsappMessage = message || 'Hola! Me gustaría contactarme con el equipo de Showroom Isabella.';
  const whatsappUrl = createWhatsAppLink(whatsappMessage);
  window.open(whatsappUrl, '_blank');
};

onMounted(() => {
  // Listener para cerrar el chat con Escape
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isChatOpen.value) {
      isChatOpen.value = false;
    }
  };

  document.addEventListener('keydown', handleEscape);

  // Cleanup
  return () => {
    document.removeEventListener('keydown', handleEscape);
  };
});
</script>

<style scoped>
.chatbot-container {
  /* Estilos específicos del chatbot si son necesarios */
}

/* Animación para el botón flotante */
@keyframes bounce {

  0%,
  20%,
  53%,
  80%,
  100% {
    transform: translate3d(0, 0, 0);
  }

  40%,
  43% {
    transform: translate3d(0, -8px, 0);
  }

  70% {
    transform: translate3d(0, -4px, 0);
  }

  90% {
    transform: translate3d(0, -2px, 0);
  }
}

/* Scroll personalizado para el área de mensajes */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
