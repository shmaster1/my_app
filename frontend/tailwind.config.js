/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
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
