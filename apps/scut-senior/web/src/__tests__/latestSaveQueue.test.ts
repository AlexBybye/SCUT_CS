import { describe, expect, it } from "vitest";
import { createLatestSaveQueue } from "../latestSaveQueue";

function deferred<T = void>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  const promise = new Promise<T>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

async function flushMicrotasks(times = 3): Promise<void> {
  for (let i = 0; i < times; i += 1) await Promise.resolve();
}

describe("latestSaveQueue", () => {
  it("串行化保存：前一个请求完成后才执行下一个", async () => {
    const queue = createLatestSaveQueue();
    const order: string[] = [];
    const first = deferred();

    queue.submit(async () => {
      order.push("first-start");
      await first.promise;
      order.push("first-end");
    });
    await flushMicrotasks();
    expect(order).toEqual(["first-start"]);

    // 第一个请求完成后，第二个才开始执行。
    first.resolve();
    await flushMicrotasks();
    expect(order).toEqual(["first-start", "first-end"]);

    queue.submit(async () => {
      order.push("second-start");
    });
    await queue.idle();
    expect(order).toEqual(["first-start", "first-end", "second-start"]);
  });

  it("合并排队中的过期快照：只提交最新一次", async () => {
    const queue = createLatestSaveQueue();
    const saved: number[] = [];

    queue.submit(async () => {
      saved.push(1);
    });
    queue.submit(async () => {
      saved.push(2);
    });
    queue.submit(async () => {
      saved.push(3);
    });

    await queue.idle();
    expect(saved).toEqual([3]);
  });

  it("在途请求完成时序号过期则补发最新快照", async () => {
    const queue = createLatestSaveQueue();
    const saved: string[] = [];
    let current = "first";
    const first = deferred();

    // save 读取调用时刻的最新快照（与 useAppStore 的 buildPreferenceSnapshot 一致）。
    queue.submit(async () => {
      saved.push(current);
      await first.promise;
    });
    await flushMicrotasks();
    expect(saved).toEqual(["first"]);

    // 第一个请求在途期间产生更新快照并触发新提交。
    current = "latest";
    queue.submit(async () => {
      saved.push("second-submit");
    });
    first.resolve();

    await queue.idle();
    // 旧请求完成后发现序号过期，补发一次最新快照；后续排队请求继续执行。
    expect(saved).toEqual(["first", "latest", "second-submit"]);
  });

  it("单个请求失败不阻断队列，后续保存继续执行", async () => {
    const queue = createLatestSaveQueue();
    const saved: string[] = [];
    const first = deferred();

    queue.submit(async () => {
      await first.promise;
      throw new Error("boom");
    });
    await flushMicrotasks();
    queue.submit(async () => {
      saved.push("ok");
    });

    first.resolve();
    await queue.idle();
    expect(saved).toEqual(["ok"]);
  });
});
