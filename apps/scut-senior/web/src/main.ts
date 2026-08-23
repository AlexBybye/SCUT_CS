import { createApp } from "vue";
// 基础样式先于组件加载，保证共享原语/令牌的级联顺序稳定。
import "./styles.css";
import App from "./App.vue";

// 注意：KaTeX（JS 与 CSS）不在此处全局引入。它只被异步加载的回答渲染视图
// （WorkflowResult → markdown.ts）消费，迭代 7.5 起按路由级随该异步块下载，
// 避免把约 75 kB gzip 的数学渲染依赖压进首屏入口包。

createApp(App).mount("#app");
