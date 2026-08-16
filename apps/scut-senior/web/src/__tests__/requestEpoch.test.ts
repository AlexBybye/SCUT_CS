import { describe, expect, it } from "vitest";
import { createRequestEpoch } from "../requestEpoch";

describe("request epoch", () => {
  it("失效后拒绝退出前创建的迟到请求快照", () => {
    const epoch = createRequestEpoch();
    const pendingRequest = epoch.snapshot();

    expect(epoch.isCurrent(pendingRequest)).toBe(true);
    epoch.invalidate();
    expect(epoch.isCurrent(pendingRequest)).toBe(false);
    expect(epoch.isCurrent(epoch.snapshot())).toBe(true);
  });
});
