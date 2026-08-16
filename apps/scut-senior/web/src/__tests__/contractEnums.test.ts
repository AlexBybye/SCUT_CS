import { describe, expect, it } from "vitest";
import sharedEnums from "../../../packages/contracts/v1/enums.json";
import {
  ANSWER_BLOCK_TYPES,
  ANSWER_MODES,
  ANSWER_STATUSES,
  COURSE_SCOPES,
  EVIDENCE_STATUSES,
  HELP_LEVELS,
  KNOWLEDGE_SCOPES,
  MODEL_SOURCES,
  RUN_STATUSES,
  TONES,
  TRACE_EVENT_STATUSES,
  WORKFLOW_TYPES,
} from "../contracts";

describe("shared V1 enums", () => {
  it("keeps the Vue contract arrays aligned with enums.json", () => {
    expect([...WORKFLOW_TYPES]).toEqual(sharedEnums.workflow_type);
    expect([...ANSWER_MODES]).toEqual(sharedEnums.answer_mode);
    expect([...TONES]).toEqual(sharedEnums.tone);
    expect([...KNOWLEDGE_SCOPES]).toEqual(sharedEnums.knowledge_scope);
    expect([...COURSE_SCOPES]).toEqual(sharedEnums.course_scope);
    expect([...MODEL_SOURCES]).toEqual(sharedEnums.model_source);
    expect([...RUN_STATUSES]).toEqual(sharedEnums.run_status);
    expect([...ANSWER_STATUSES]).toEqual(sharedEnums.answer_status);
    expect([...EVIDENCE_STATUSES]).toEqual(sharedEnums.evidence_status);
    expect([...ANSWER_BLOCK_TYPES]).toEqual(sharedEnums.answer_block_type);
    expect([...TRACE_EVENT_STATUSES]).toEqual(sharedEnums.trace_event_status);
    expect([...HELP_LEVELS]).toEqual(sharedEnums.help_level);
    expect(sharedEnums.bilibili_review_status).toEqual(["unreviewed_live_search"]);
  });
});
