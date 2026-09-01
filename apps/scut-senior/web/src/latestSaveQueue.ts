/**
 * 串行化并合并「只关心最新状态」的保存请求。
 *
 * 多个 watcher 会在短时间内连续触发同一种保存（如账户偏好）。本队列：
 *
 * - 单尾 promise 串行化：同一时刻最多一个请求在途，杜绝旧请求后到覆盖新状态；
 * - 新请求只提交最新快照：排队时直接读取调用时刻的最新值，中间态不会被重复提交；
 * - 旧请求完成后若发现已产生更新的请求（序号过期），补发一次最新快照，
 *   保证服务端收敛到最终状态；
 * - 失败一律非阻断：单个请求失败不会中断队列，也不会抛出到调用方。
 */
export interface LatestSaveQueue {
  /** 排队一次保存；`save` 应读取调用时刻的最新快照。 */
  submit(save: () => Promise<void>): void;
  /** 等待队列排空（含补发），测试与退出前收敛使用。 */
  idle(): Promise<void>;
}

export function createLatestSaveQueue(): LatestSaveQueue {
  let sequence = 0;
  let tail: Promise<void> = Promise.resolve();

  function run(save: () => Promise<void>, current: number): Promise<void> {
    if (current !== sequence) {
      // 已有更新的保存请求排队：本轮跳过，由最新请求提交，避免堆积中间态。
      return Promise.resolve();
    }
    return Promise.resolve()
      .then(save)
      .catch(() => {
        // 保存失败非阻断：本地即时体验保留，下一次改动会再次触发。
      })
      .then(() => {
        if (current !== sequence) {
          // 在途期间产生了更新的快照：补发一次最新快照让服务端收敛。
          return Promise.resolve()
            .then(save)
            .catch(() => {
              // 补发失败同样非阻断。
            });
        }
      });
  }

  return {
    submit(save) {
      const current = ++sequence;
      tail = tail.catch(() => undefined).then(() => run(save, current));
    },
    idle() {
      return tail.catch(() => undefined);
    },
  };
}
