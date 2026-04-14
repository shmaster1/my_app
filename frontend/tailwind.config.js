/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out both",
      },
      fontFamily: {
        display: ["'Bebas Neue'", "cursive"],
        body: ["'DM Sans'", "sans-serif"],
      },
      colors: {
        ink: "#0f0f0f",
        ash: "#f4f3f0",
        mist: "#e8e6e1",
        fog: "#c8c5be",
        accent: "#2a2a2a",
        pop: "#d4a853",
      },
    },
  },
  plugins: [],
};
