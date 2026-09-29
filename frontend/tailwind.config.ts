import type { Config } from "tailwindcss";
const config: Config = { content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: { colors: { forest: "#15372e", moss: "#6e8b69", paper: "#f5f4ef" } } }, plugins: [] };
export default config;
