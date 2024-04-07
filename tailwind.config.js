// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        glitch: 'glitch 1s infinite',
        'glitch-reverse': 'glitch-reverse 1s infinite',
      },
      keyframes: {
        glitch: {
          '0%': { opacity: 1, transform: 'translate(0)' },
          '50%': { opacity: 0, transform: 'translate(0.5rem, -0.2rem)' },
          '100%': { opacity: 1, transform: 'translate(0)' },
        },
        'glitch-reverse': {
          '0%': { opacity: 1, transform: 'translate(0)' },
          '50%': { opacity: 0, transform: 'translate(-0.5rem, 0.2rem)' },
          '100%': { opacity: 1, transform: 'translate(0)' },
        },
      },
    },
  },
  variants: {
    extend: {
      animation: ['hover', 'focus'],
    },
  },
  plugins: [],
};
