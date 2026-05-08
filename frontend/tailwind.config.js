/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#113655",
          hover: "#0c263c",
          light: "#1a4a73",
          dark: "#0a2036",
          muted: "rgba(17,54,85,0.06)",
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
          hover: "#9abdd6",
          light: "#dce9f3",
          muted: "rgba(179,205,225,0.15)",
        },
        brand: {
          navy: "#113655",
          light: "#B3CDE1",
          bg: "#F4F6F8",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        heading: ["Arboria", "DM Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "SF Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        "card": "0 1px 2px rgba(17,54,85,0.05)",
        "card-hover": "0 4px 16px rgba(17,54,85,0.08)",
        "e1": "0 1px 2px rgba(17,54,85,0.05)",
        "e2": "0 2px 8px rgba(17,54,85,0.06), 0 1px 2px rgba(17,54,85,0.04)",
        "e3": "0 6px 20px rgba(17,54,85,0.08), 0 2px 4px rgba(17,54,85,0.04)",
        "e4": "0 12px 40px rgba(17,54,85,0.12), 0 4px 8px rgba(17,54,85,0.05)",
      },
      borderRadius: {
        'xs': '2px',
        DEFAULT: '3px',
        'md': '4px',
        'lg': '6px',
        'xl': '8px',
      },
    },
  },
  plugins: [],
};
