import { describe, expect, it } from "vitest";
import { createBottomFollower } from "../scrollFollow";

// force 经由 nextTick 写入，断言前先让微任务排空。
const flush = () => new Promise<void>((resolve) => setTimeout(resolve, 0));

describe("createBottomFollower", () => {
  it("无 DOM 环境（node 测试环境）下 start/stop/force 都是安全空操作", () => {
    const follower = createBottomFollower(() => null, 500, { shouldFollow: () => true });
    expect(() => {
      follower.start();
      follower.start(); // 幂等：不会叠加第二个 interval
      follower.force();
      follower.stop();
      follower.stop(); // 幂等
    }).not.toThrow();
  });

  it("shouldFollow 为真时 force 贴底，为假时不改写 scrollTop", async () => {
    const following = { scrollHeight: 400, scrollTop: 0, clientHeight: 100 };
    createBottomFollower(() => following as unknown as HTMLElement, 500, {
      shouldFollow: () => true,
    }).force();
    await flush();
    expect(following.scrollTop).toBe(400);

    const pinnedOff = { scrollHeight: 400, scrollTop: 40, clientHeight: 100 };
    createBottomFollower(() => pinnedOff as unknown as HTMLElement, 500, {
      shouldFollow: () => false,
    }).force();
    await flush();
    expect(pinnedOff.scrollTop).toBe(40);
  });

  it("未提供 shouldFollow 时无条件贴底", async () => {
    const el = { scrollHeight: 400, scrollTop: 0, clientHeight: 100 };
    createBottomFollower(() => el as unknown as HTMLElement, 500).force();
    await flush();
    expect(el.scrollTop).toBe(400);
  });
});
