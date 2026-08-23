"""§13.1.1 probe verdict report for the glm-4.6V waiver-queue rerun.

Reads the isolated probe results file plus the rerun target list and prints
the judgment table required by CODE_ITERATION_SOP v1.9 §13.1.1 / §12A Group D:

  - completed images (api-error lines are excluded; they are retried on resume)
  - three-gate outcome distribution (majority+render / unsure / no-math /
    disagree / implausible-or-render)
  - acceptance rate vs the pre-set 85% threshold
  - capability split: formula-bearing failures vs correct abstentions
    (unsure / no-math-content are treated as candidate correct abstentions
    because the waived queue contains known non-formula page decorations)
  - per-course breakdown

Usage:
    python3 probe_report.py [results.jsonl] [targets.json]
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

JOBS = Path(__file__).resolve().parent / ".ai_jobs"
RESULTS = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    JOBS / "_vision_results_glm46v_probe.jsonl"
)
TARGETS = Path(sys.argv[2]) if len(sys.argv) > 2 else (
    JOBS / "_waiver_rerun_targets.json"
)
THRESHOLD_ACCEPT = 0.85


def course_of(path: str) -> str:
    parts = Path(path).parts
    try:
        return parts[parts.index("knowledge") + 1]
    except (ValueError, IndexError):
        return "?"


def main() -> int:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    total_targets = len(targets)

    latest: dict[str, dict] = {}
    api_errors = 0
    for line in RESULTS.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if str(r.get("why", "")).startswith("api-error"):
            api_errors += 1
            continue
        latest[r["path"]] = r

    outcomes = Counter(r["why"] for r in latest.values())
    completed = len(latest)
    accepted = outcomes.get("majority+render", 0)

    # non-formula abstentions: model said UNSURE or reported no math content;
    # these waive correctly rather than counting as transcription failures
    correct_abstain = outcomes.get("unsure", 0) + outcomes.get("no-math-content", 0)
    formula_failures = (
        outcomes.get("disagree", 0)
        + outcomes.get("implausible-or-render", 0)
    )

    by_course: dict[str, Counter[str]] = defaultdict(Counter)
    for path, r in latest.items():
        by_course[course_of(path)][r["why"]] += 1

    rate = accepted / completed if completed else 0.0
    print(f"targets(total waiver queue): {total_targets}")
    print(f"completed(excl. api-error): {completed}   api-error(retry pending): {api_errors}")
    print(f"outcomes: {dict(outcomes)}")
    print(f"accepted: {accepted}  ->  gate pass rate {rate:.1%}  (threshold >= {THRESHOLD_ACCEPT:.0%})")
    denom2 = completed - correct_abstain
    if denom2 > 0:
        print(
            f"capability view: {accepted}/{denom2} of formula-bearing images "
            f"= {accepted / denom2:.1%} (correct abstentions excluded: {correct_abstain})"
        )
    print("per-course:")
    for course, cnt in sorted(by_course.items(), key=lambda kv: -sum(kv[1].values())):
        ok = cnt.get("majority+render", 0)
        print(f"  {course:34s} total={sum(cnt.values()):4d} accepted={ok:4d} {dict(cnt)}")

    remaining = total_targets - completed - api_errors
    print(f"remaining(including retries): {remaining}")
    verdict = "PASS" if rate >= THRESHOLD_ACCEPT else "BELOW_THRESHOLD"
    print(f"SOP §13.1.1 probe gate (preset 85%): {verdict}"
          f"{'  (final)' if remaining == 0 and api_errors == 0 else '  (interim)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
