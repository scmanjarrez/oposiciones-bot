/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        vigente: '#22c55e',
        desfasada: '#f59e0b',
        derogada: '#ef4444',
        erronea: '#a855f7',
      },
    },
  },
  plugins: [],
}
