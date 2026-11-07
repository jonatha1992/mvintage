// Configuración centralizada y mínima del frontend.
// Principios:
// 1. Fail-fast en build (no dev) si falta una variable obligatoria.
// 2. Fallbacks solo para desarrollo local.
// 3. Objeto único exportado (config) para facilitar refactors.

const isDev = import.meta.env.VITE_ENVIRONMENT === 'dev';

function required(name: string, fallback?: string): string {
    const value = (import.meta.env as any)[name] as string | undefined;
    if (value) return value;
    if (isDev && fallback) return fallback; // Permite trabajar rápido en dev.
    throw new Error(`[config] Variable requerida no definida: ${name}`);
}

const backendUrl = required('VITE_BACKEND_URL', 'http://localhost:8000/api/v1');

export const config = Object.freeze({
    backendUrl,
    firebase: {
        apiKey: (import.meta.env as any).VITE_API_KEY || '',
        authDomain: (import.meta.env as any).VITE_AUTH_DOMAIN || '',
        projectId: (import.meta.env as any).VITE_PROJECT_ID || '',
        storageBucket: (import.meta.env as any).VITE_STORAGE_BUCKET || '',
        messagingSenderId: (import.meta.env as any).VITE_MESSAGING_SENDER_ID || '',
        appId: (import.meta.env as any).VITE_APP_ID || '',
    }
});

export type AppConfig = typeof config;
export default config;