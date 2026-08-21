import { nextTick } from "vue";

/**
 * 滚动容器「贴底跟随」：记录区大滚动条与 trace 内滚共用的同一套机制。
 *
 * 追踪不挂在逐个内容事件上，而是 interval 轮询——流式 delta、trace 步进这类
 * 高频追加因此天然被节流为每 intervalMs 至多一次 scrollTop 写入。
 *
 * 是否跟随由可选的 shouldFollow 在每次写入前评估。注意判据必须反映用户意图
 * （例如只在用户 scroll 事件里更新的 pinned 标记），不能直接量「当前离底部的
 * 距离」：内容追加本身会把距离撑大，跟随会刚起步就自我关闭、再也追不上。
 */

export interface BottomFollower {
  /** 开始周期性贴底；已在跟随时幂等。 */
  start(): void;
  /** 停止周期性贴底；未在跟随时是空操作。 */
  stop(): void;
  /** 跳过节流立即执行一次跟随写入（DOM 更新后）；仍受 shouldFollow 门控。 */
  force(): void;
}

export function createBottomFollower(
  getEl: () => HTMLElement | null,
  intervalMs: number,
  options: { shouldFollow?: () => boolean } = {},
): BottomFollower {
  let timer: number | null = null;

  function scrollToBottom(): void {
    if (options.shouldFollow && !options.shouldFollow()) return;
    const el = getEl();
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }

  return {
    start() {
      if (timer !== null || typeof window === "undefined") return;
      timer = window.setInterval(() => {
        void nextTick(scrollToBottom);
      }, intervalMs);
    },
    stop() {
      if (timer !== null) {
        window.clearInterval(timer);
        timer = null;
      }
    },
    force() {
      void nextTick(scrollToBottom);
    },
  };
}
