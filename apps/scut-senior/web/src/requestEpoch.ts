export interface RequestEpoch {
  snapshot(): number;
  invalidate(): number;
  isCurrent(snapshot: number): boolean;
}

export function createRequestEpoch(): RequestEpoch {
  let epoch = 0;

  return {
    snapshot: () => epoch,
    invalidate: () => {
      epoch += 1;
      return epoch;
    },
    isCurrent: (snapshot) => snapshot === epoch,
  };
}
