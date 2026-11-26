/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}"
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#1e3a8a',
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                    950: '#172554',
                },
                secondary: {
                    DEFAULT: '#f8fafc',
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155',
                    800: '#1e293b',
                    900: '#0f172a',
                    950: '#020617',
                },
                accent: {
                    DEFAULT: '#3b82f6',
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                },
                'body-text': '#4b5563'
            },
            fontFamily: {
                sans: ['Lato', 'ui-sans-serif', 'system-ui', 'sans-serif'],
                mono: ['Roboto Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
                heading: ['Lato', 'ui-sans-serif', 'system-ui', 'sans-serif'],
                body: ['Roboto Mono', 'ui-monospace', 'SFMono-Regular', 'monospace']
            },
            fontSize: {
                'base': ['14px', '1.6'],
                'h1': ['28px', '1.2'],
                'h2': ['24px', '1.2'],
                'h3': ['20px', '1.2'],
                'h4': ['18px', '1.2'],
                'h5': ['16px', '1.2'],
                'h6': ['14px', '1.2']
            }
        }
    },
    plugins: []
}
