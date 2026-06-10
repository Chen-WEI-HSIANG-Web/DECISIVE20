import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: Vite serves the UI and proxies /api to the FastAPI backend (port 8000).
// Build: output goes straight into the package's static dir so uvicorn serves it.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  build: {
    outDir: "../decisive20/web/static",
    emptyOutDir: true,
  },
});
