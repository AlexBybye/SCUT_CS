import vue from "@vitejs/plugin-vue";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");

  return {
    plugins: [vue()],
    server: {
      allowedHosts: ["by9000p.tail26d033.ts.net"],
      // A Funnel terminates TLS on 443 while Vite listens locally on 5173.
      // Tell public clients to reconnect through the Funnel instead of trying
      // their own localhost for hot-module reload.
      hmr: {
        protocol: "wss",
        host: "by9000p.tail26d033.ts.net",
        clientPort: 443,
      },
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
