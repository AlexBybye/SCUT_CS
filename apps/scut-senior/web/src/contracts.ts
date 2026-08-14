export const WORKFLOW_TYPES = [
  "knowledge_qa",
  "exam_review",
  "problem_tutor",
  "mistake_review",
  "temporary_material_reading",
] as const;

export const ANSWER_MODES = [
  "concise",
  "detailed",
  "example",
  "step_by_step",
] as const;

export const TONES = [
  "teaching_assistant",
  "study_partner",
  "senior_student",
] as const;

export const KNOWLEDGE_SCOPES = ["course_only", "course_first"] as const;

export const COURSE_SCOPES = ["single", "cross"] as const;

export const MODEL_SOURCES = ["platform_default", "user_key"] as const;

export const RUN_STATUSES = [
  "created",
  "running",
  "completed",
  "interrupted",
  "failed",
] as const;

export const ANSWER_STATUSES = [
  "answered",
  "partial",
  "insufficient_evidence",
  "needs_clarification",
  "refused",
  "error",
] as const;

export const EVIDENCE_STATUSES = [
  "sufficient",
  "partial",
  "insufficient",
  "not_evaluated",
] as const;

export const TRACE_EVENT_STATUSES = [
  "started",
  "completed",
  "failed",
  "skipped",
] as const;

export const ANSWER_BLOCK_TYPES = [
  "repository",
  "user_material",
  "general",
  "personalized_analysis",
] as const;

export const HELP_LEVELS = [
  "concept",
  "approach",
  "step_by_step",
  "full_explanation",
  "answer_analysis",
] as const;

export type WorkflowType = (typeof WORKFLOW_TYPES)[number];
export type AnswerMode = (typeof ANSWER_MODES)[number];
export type Tone = (typeof TONES)[number];
export type KnowledgeScope = (typeof KNOWLEDGE_SCOPES)[number];
export type HelpLevel = (typeof HELP_LEVELS)[number];
export type RunStatus = (typeof RUN_STATUSES)[number];
export type AnswerStatus = (typeof ANSWER_STATUSES)[number];
export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number];
export type AnswerBlockType = (typeof ANSWER_BLOCK_TYPES)[number];
export type CourseScope = (typeof COURSE_SCOPES)[number];
export type ModelSource = (typeof MODEL_SOURCES)[number];
export type TraceEventStatus = (typeof TRACE_EVENT_STATUSES)[number];
export type LocatorType = "page" | "slide" | "heading" | "question" | "none";

export interface Course {
  course_id: string;
  display_name: string;
  aliases: string[];
  is_open: boolean;
  mock_available: boolean;
}

export interface KnowledgeQaPayload {
  question: string;
}

export interface ExamReviewPayload {
  syllabus?: string;
  exam_date?: string;
  available_hours?: number;
  goals: string[];
  weak_topics: string[];
}

export interface ProblemTutorPayload {
  problem: string;
  user_answer?: string;
  help_level: HelpLevel;
  problem_source?: string;
}

export interface MistakeReviewPayload {
  problem: string;
  original_answer: string;
  reference_answer?: string;
  review_focus?: string;
}

export interface TemporaryMaterialReadingPayload {
  material_text: string;
  reading_goal?: string;
}

export interface WorkflowPayloadMap {
  knowledge_qa: KnowledgeQaPayload;
  exam_review: ExamReviewPayload;
  problem_tutor: ProblemTutorPayload;
  mistake_review: MistakeReviewPayload;
  temporary_material_reading: TemporaryMaterialReadingPayload;
}

export type WorkflowPayload = WorkflowPayloadMap[WorkflowType];

export interface WorkflowRunRequest<T extends WorkflowType = WorkflowType> {
  workflow_type: T;
  course_scope: CourseScope;
  course_id: string | null;
  allowed_course_ids: string[];
  conversation_id: string;
  model_source: ModelSource;
  provider_id: string;
  model_id: string;
  user_input: string;
  answer_mode: AnswerMode;
  tone: Tone;
  knowledge_scope: KnowledgeScope;
  include_bilibili_resources: boolean;
  context_refs: string[];
  attachments: Record<string, unknown>[];
  workflow_payload: WorkflowPayloadMap[T];
}

export interface Citation {
  citation_id: string;
  chunk_id: string;
  course_id: string;
  course_title: string;
  source_id: string;
  source_title: string;
  locator_type: LocatorType;
  locator_start?: string | number | null;
  locator_end?: string | number | null;
  question_id?: string | null;
  heading_path?: string[];
}

export interface ExternalResource {
  resource_id?: string | null;
  course_id: string;
  platform: "bilibili";
  resource_type: "video" | "search";
  title: string;
  url: string;
  matched_topic: string;
  review_status: "reviewed" | "pending" | "rejected" | "unavailable";
  catalog_version?: string | null;
  evidence_role: "supplementary_only";
}

export interface TraceSourceSummary {
  course_id: string;
  title: string;
  locator?: string | number | null;
}

export interface TraceSafeResult {
  workflow_type?: WorkflowType | null;
  course_scope?: CourseScope | null;
  course_ids?: string[] | null;
  knowledge_scope?: KnowledgeScope | null;
  mode?: "mock" | "synthetic_fixture_only" | null;
  hit_count?: number | null;
  sources?: TraceSourceSummary[] | null;
  rewritten_query?: string | null;
  candidate_order?: string[] | null;
  reranked_order?: string[] | null;
  evidence_status?: EvidenceStatus | null;
  used_general_knowledge?: boolean | null;
  model_source?: ModelSource | null;
  provider_id?: string | null;
  model_id?: string | null;
  billing_label?: string | null;
  availability_status?: string | null;
  real_model_called?: boolean | null;
  cache_hit?: boolean | null;
  retry_count?: number | null;
  failure_code?: string | null;
  degradation_code?: string | null;
  catalog_version?: string | null;
  fixture_only?: boolean | null;
  normalized_topics?: string[] | null;
  unreviewed_search_returned?: boolean | null;
  reason_code?: string | null;
  candidate_count?: number | null;
  accepted_count?: number | null;
  external_resources_separate?: boolean | null;
  stored?: boolean | null;
  adapter?: "sqlite_mock" | null;
}

export interface TraceEvent {
  event_id: string;
  sequence: number;
  node: string;
  status: TraceEventStatus;
  duration_ms: number;
  result: TraceSafeResult;
}

export interface WorkflowRunResult {
  workflow_run_id: string;
  conversation_id: string;
  message_id: string;
  answer_id: string;
  run_status: RunStatus;
  answer_status: AnswerStatus;
  workflow_type: WorkflowType;
  course_scope: CourseScope;
  course_ids: string[];
  repository_answer: string | null;
  general_supplement: string | null;
  answer_blocks: AnswerBlock[];
  workflow_output: Record<string, unknown>;
  evidence_status: EvidenceStatus;
  citations: Citation[];
  related_topics: string[];
  related_questions: string[];
  external_resources: ExternalResource[];
  trace: TraceEvent[];
  coverage_gaps: string[];
  corpus_version: string;
  course_pack_version: string | null;
  workflow_version: string;
  model_source: ModelSource;
  model: ModelMetadata;
  availability_status: string;
}

export interface AnswerBlock {
  type: AnswerBlockType;
  content: string;
}

export interface ModelMetadata {
  provider_id: string;
  model_id: string;
  billing_label: string;
  mock_only: boolean;
}

export interface Conversation {
  conversation_id: string;
  user_id: string;
  course_id: string;
  created_at: string;
  mock_only: boolean;
  runs?: WorkflowRunResult[];
}
