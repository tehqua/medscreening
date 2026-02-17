import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite config: proxies /api calls to the FastAPI backend running on port 8000.
// This avoids CORS issues in development.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
