import type { Config } from "tailwindcss";

export default {
  darkMode: 'class',
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "aurora-blue": "#0066FF",
        "aurora-purple": "#7C3AED",
        "aurora-pink": "#FF1493",
        "aurora-cyan": "#00D9FF",
        "aurora-lime": "#00FF41",
        "aurora-orange": "#FF6B35",
        "aurora-teal": "#00CED1",
      },
      backgroundImage: {
        'gradient-aurora': 'linear-gradient(135deg, #0066FF 0%, #7C3AED 50%, #FF1493 100%)',
        'gradient-cyan-lime': 'linear-gradient(135deg, #00D9FF 0%, #00FF41 100%)',
        'gradient-pink-purple': 'linear-gradient(135deg, #FF1493 0%, #7C3AED 100%)',
      },
      fontFamily: {
        sans: ['Inter', 'San Francisco', 'helvetica', 'arial', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(0, 102, 255, 0.7)' },
          '50%': { boxShadow: '0 0 0 10px rgba(0, 102, 255, 0)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
    }
  },
  plugins: [],
} satisfies Config;
