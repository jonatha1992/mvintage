import { ref, readonly, computed } from 'vue';
import { debounce } from '../utils/debounce';

// Estado global del loading
const isLoading = ref(false);
const loadingMessage = ref('');
const loadingSubmessage = ref('');
const routeLoading = ref(false);

export function useLoading() {
  const showLoading = (message: string, submessage?: string) => {
    loadingMessage.value = message;
    loadingSubmessage.value = submessage || '';
    isLoading.value = true;
  };

  const hideLoading = () => {
    isLoading.value = false;
    loadingMessage.value = '';
    loadingSubmessage.value = '';
  };

  const setLoadingMessage = (message: string, submessage?: string) => {
    loadingMessage.value = message;
    loadingSubmessage.value = submessage || '';
  };

  const showRouteLoading = (message: string, submessage?: string) => {
    routeLoading.value = true;
    showLoading(message, submessage);
  };
  const hideRouteLoading = () => {
    routeLoading.value = false;
    hideLoading();
  };
  const isRouteLoading = computed(() => routeLoading.value);

  // NOTA: showSmartLoading ya no se usa para navegación de rutas,
  // solo para operaciones específicas como agregar al carrito, etc.
  // La navegación de rutas ahora usa ProgressBar (globalProgressBar).

  // Loading inteligente - solo muestra loading si la operación tarda más del umbral
  const showSmartLoading = (
    promise: Promise<any>,
    message: string = 'Cargando...',
    threshold: number = 200
  ) => {
    let timeoutId: NodeJS.Timeout | null = null;
    let loadingShown = false;

    // Mostrar loading solo si tarda más del umbral
    timeoutId = setTimeout(() => {
      showLoading(message);
      loadingShown = true;
    }, threshold);

    return promise.finally(() => {
      // Limpiar timeout si la operación terminó rápido
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      // Ocultar loading solo si se mostr
      if (loadingShown) {
        hideLoading();
      }
    });
  };

  // Loading debounced para evitar flicker en operaciones rápidas consecutivas
  const debouncedShowLoading = debounce((message: string, submessage?: string) => {
    showLoading(message, submessage);
  }, 100);

  const debouncedHideLoading = debounce(() => {
    hideLoading();
  }, 50);

  return {
    isLoading: readonly(isLoading),
    loadingMessage: readonly(loadingMessage),
    loadingSubmessage: readonly(loadingSubmessage),
    isRouteLoading,
    showLoading,
    hideLoading,
    showRouteLoading,
    hideRouteLoading,
    setLoadingMessage,
    showSmartLoading,
    debouncedShowLoading,
    debouncedHideLoading
  };
}