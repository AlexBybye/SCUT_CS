import { createApp } from "vue";
// 基础样式先于组件加载，保证共享原语/令牌的级联顺序稳定。
import "./styles.css";
import "katex/dist/katex.min.css";
import App from "./App.vue";

createApp(App).mount("#app");
