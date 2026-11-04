/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#04060d",
          900: "#070b16",
          800: "#0b1120",
          700: "#111a2e",
        },
        accent: {
          DEFAULT: "#22d3ee",
          soft: "#67e8f9",
          mint: "#34d399",
        },
        risk: {
          low: "#34d399",
          medium: "#fbbf24",
          high: "#fb923c",
          critical: "#f43f5e",
          uncertain: "#a78bfa",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px -12px rgba(34, 211, 238, 0.45)",
        card: "0 18px 40px -24px rgba(0, 0, 0, 0.9)",
      },
      backgroundImage: {
        "mesh-radial":
          "radial-gradient(900px circle at 12% -10%, rgba(34,211,238,0.16), transparent 45%), radial-gradient(800px circle at 88% 0%, rgba(52,211,153,0.12), transparent 40%), radial-gradient(700px circle at 50% 110%, rgba(167,139,250,0.12), transparent 45%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.95)", opacity: "0.7" },
          "70%": { transform: "scale(1.15)", opacity: "0" },
          "100%": { opacity: "0" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.4s ease-out both",
        "pulse-ring": "pulse-ring 2.4s cubic-bezier(0.4,0,0.6,1) infinite",
      },
    },
  },
  plugins: [],
};
