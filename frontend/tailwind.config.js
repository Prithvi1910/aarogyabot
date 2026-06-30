/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        // Calm, minimal teal brand palette
        brand: {
          50: '#f0fbfa',
          100: '#d9f4f2',
          200: '#b4e8e5',
          300: '#84d6d2',
          400: '#4cbcb9',
          500: '#2aa3a1',
          600: '#1d8584',
          700: '#1c6a6b',
          800: '#1b5557',
          900: '#0e3739',
        },
        ink: {
          900: '#0f2a2b',
          700: '#33514f',
          500: '#5b756f',
        },
      },
      boxShadow: {
        soft: '0 6px 24px -10px rgba(14, 55, 57, 0.18)',
        card: '0 12px 34px -16px rgba(14, 55, 57, 0.28)',
        glow: '0 12px 30px -8px rgba(29, 133, 132, 0.45)',
        frame: '0 30px 80px -30px rgba(14, 55, 57, 0.45)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      keyframes: {
        floaty: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        popIn: {
          '0%': { opacity: '0', transform: 'scale(0.96) translateY(6px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
      },
      animation: {
        floaty: 'floaty 6s ease-in-out infinite',
        'pop-in': 'popIn 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
      },
    },
  },
  plugins: [],
}
