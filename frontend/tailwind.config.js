/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#113655",
          hover: "#0e2d47",
          50: "#f0f5fa",
          100: "#dce9f4",
          200: "#b3cde1",
          300: "#8ab1ce",
          400: "#6095bb",
          500: "#3779a8",
          600: "#2a618a",
          700: "#1e4a6b",
          800: "#113655",
          900: "#0a2036",
        },
        accent: {
          DEFAULT: "#B3CDE1",
          hover: "#a2bad1",
        },
        brand: {
          navy: "#113655",
          light: "#B3CDE1",
          bg: "#F8FAFC",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        heading: ["Arboria", "Inter", "system-ui", "sans-serif"],
        display: ["'KG Second Chances Sketch'", "cursive"],
      },
      boxShadow: {
        "card": "0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px 0 rgba(0,0,0,0.06)",
        "card-hover": "0 10px 25px -3px rgba(17,54,85,0.12), 0 4px 6px -2px rgba(17,54,85,0.05)",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
      },
    },
  },
  plugins: [],
};
