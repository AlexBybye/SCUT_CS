import vue from "@vitejs/plugin-vue";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");

  return {
    plugins: [vue()],
    server: {
      allowedHosts: ["alex-3.tail26d033.ts.net"],
      proxy: {
        "/api": {
          target: env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
    test: {
      environment: "node",
      include: ["src/**/*.test.ts"],
    },
  };
});