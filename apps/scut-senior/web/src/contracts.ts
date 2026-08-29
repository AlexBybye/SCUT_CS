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

export const FEEDBACK_TYPES = [
  "helpful",
  "not_helpful",
  "knowledge_error",
  "did_not_answer",
] as const;

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
export type FeedbackType = (typeof FEEDBACK_TYPES)[number];
export type TraceEventStatus = (typeof TRACE_EVENT_STATUSES)[number];
export type LocatorType = "page" | "slide" | "heading" | "question" | "none";

export const COURSE_PLUGIN_STATES = ["active", "fixture_only", "registered"] as const;
export type CoursePluginState = (typeof COURSE_PLUGIN_STATES)[number];

export const COURSE_CATEGORIES = ["enabled", "not_enabled", "no_data"] as const;
export type CourseCategory = (typeof COURSE_CATEGORIES)[number];

export const RETRIEVAL_MODES = ["fixture", "local_corpus"] as const;
export const RETRIEVAL_AVAILABILITIES = [
  "fixture",
  "local_corpus",
  "unavailable",
] as const;
export type RetrievalMode = (typeof RETRIEVAL_MODES)[number];
export type RetrievalAvailability = (typeof RETRIEVAL_AVAILABILITIES)[number];

export interface AgentPresetEntry {
  preset_id: string;
  preset_version: string;
  display_name: string;
  workflow_type: WorkflowType;
  focus_strategy: string;
  allowed_tools: string[];
  required_input_modalities: string[];
  requires_structured_outputs: boolean;
}

export interface ControlledToolEntry {
  tool_id: string;
  display_name: string;
  description: string;
  model_callable: boolean;
}

export interface MaintainerSkillEntry {
  skill_id: string;
  display_name: string;
  version: string;
  description: string;
  status: "contract_only";
  human_review_required: boolean;
  can_mark_passed_or_active: boolean;
}

export interface CoursePluginEntry {
  course_id: string;
  display_name: string;
  state: CoursePluginState;
  loaded: boolean;
  usable: boolean;
  category: CourseCategory;
  enabled_workflows: WorkflowType[];
}

export interface PluginRegistry {
  registry_version: string;
  retrieval_mode: "fixture" | "local_corpus";
  agent_presets: AgentPresetEntry[];
  controlled_tools: ControlledToolEntry[];
  maintainer_skills: MaintainerSkillEntry[];
  courses: CoursePluginEntry[];
}

export interface FeedbackRecord {
  feedback_id: string;
  user_id: string;
  run_id: string;
  conversation_id: string;
  course_id: string;
  workflow_type: WorkflowType;
  feedback_type: FeedbackType;
  note: string | null;
  answer_status: AnswerStatus;
  created_at: string;
  expires_at: string;
}

export interface Course {
  course_id: string;
  display_name: string;
  aliases: string[];
  is_open: boolean;
  mock_available: boolean;
  retrieval_availability: RetrievalAvailability;
  retrieval_available: boolean;
  plugin_loaded: boolean;
  selectable: boolean;
  usable: boolean;
  category: CourseCategory;
}

export interface CourseCatalog {
  contract_version: string;
  retrieval_mode: RetrievalMode;
  courses: Course[];
}

export interface ModelCatalogItem {
  provider_id: string;
  model_id: string;
  company: string;
  display_name: string;
  model_source: ModelSource;
  billing_label: string;
  availability_status: string;
  context_length: number;
  input_modalities: string[];
  supports_structured_outputs: boolean;
  is_preview: boolean;
  user_selectable: boolean;
  last_checked_at: string | null;
}

export interface ModelCatalog {
  catalog_version: string;
  platform_credential_configured: boolean;
  real_platform_default_available: boolean;
  health_checked_at: string | null;
  byok_available: boolean;
  byok_catalog_version: string;
  byok_providers: ByokProviderCatalogItem[];
  quota_notice: string;
  quota_exhausted_message: string;
  models: ModelCatalogItem[];
}

export interface ByokModelCatalogItem {
  model_id: string;
  company: string;
  display_name: string;
}

export type ByokProviderId = "openrouter" | "deepseek" | "siliconflow" | "zhipu";

export interface ByokProviderCatalogItem {
  provider_id: ByokProviderId;
  company: string;
  display_name: string;
  enabled: boolean;
  models_confirmed: boolean;
  models: ByokModelCatalogItem[];
  custom_base_url_allowed: false;
  endpoint_policy: "fixed_provider_endpoint";
}

export interface ByokCredentialStatus {
  provider_id: ByokProviderId;
  model_id: string;
  configured: boolean;
  masked_key: string | null;
  expires_at: string | null;
  writable: boolean;
  source: "user_key";
  updated_at: string | null;
}

export interface AuthUser {
  user_id: string;
  display_name: string;
  auth_mode: "mock" | "github_oauth";
  is_mock: boolean;
  github_login: string | null;
  session_expires_at: string | null;
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
  material_title?: string;
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
  resource_id: null;
  course_id: string;
  platform: "bilibili";
  resource_type: "search";
  title: string;
  url: string;
  matched_topic: string;
  review_status: "unreviewed_live_search";
  catalog_version: null;
  query_keywords: string[];
  generated_at: string;
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
  auth_mode?: "mock" | "github_oauth" | null;
  agent_preset_id?: string | null;
  agent_preset_version?: string | null;
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
  review_path?: string | null;
  sample_years?: number[] | null;
  reason_code?: string | null;
  candidate_count?: number | null;
  accepted_count?: number | null;
  external_resources_separate?: boolean | null;
  stored?: boolean | null;
  adapter?: "sqlite_mock" | "sqlite" | null;
}

export interface TraceEvent {
  event_id: string;
  sequence: number;
  node: string;
  status: TraceEventStatus;
  duration_ms: number;
  result: TraceSafeResult;
}

export interface AnswerDelta {
  block_index: number;
  type: AnswerBlockType;
  delta: string;
}

export interface WorkflowStreamError {
  code: string;
  detail: string;
}

export interface AgentStreamEvent {
  event_kind: string;
  action?: string;
  status?: string;
  reason?: string;
  step_count?: number;
  observation_count?: number;
}

export type WorkflowStreamKind = "trace" | "answer_delta" | "result" | "error" | "agent";

export interface WorkflowStreamEvent {
  kind: WorkflowStreamKind;
  workflow_run_id: string | null;
  sequence: number;
  trace_event?: TraceEvent;
  answer_delta?: AnswerDelta;
  result?: WorkflowRunResult;
  error?: WorkflowStreamError;
  agent_event?: AgentStreamEvent;
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

export interface WorkflowAttempt {
  workflow_run_id: string;
  attempt_group_id: string;
  regenerated_from_run_id: string | null;
  request: WorkflowRunRequest;
  result: WorkflowRunResult;
  created_at: string;
  updated_at: string;
  expires_at: string;
}

export interface ConversationSummary {
  conversation_id: string;
  user_id: string;
  course_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  expires_at: string;
  mock_only: boolean;
}

export interface ConversationDetail extends ConversationSummary {
  runs: WorkflowAttempt[];
}

// ---------------------------------------------------------------------------
// 迭代 7（SOP §12）：临时材料精读治理与贡献待处理队列。
// ---------------------------------------------------------------------------

export type ContributionState =
  | "draft"
  | "submitted"
  | "pr_open"
  | "merged"
  | "rejected"
  | "expired";

export const CONTRIBUTION_STATES: readonly ContributionState[] = [
  "draft",
  "submitted",
  "pr_open",
  "merged",
  "rejected",
  "expired",
] as const;

export interface TemporaryMaterialRecord {
  material_id: string;
  conversation_id: string;
  course_id: string;
  title: string | null;
  char_count: number;
  content_sha256: string;
  created_at: string;
  expires_at: string;
  mock_only: boolean;
}

export interface TemporaryMaterialDetail extends TemporaryMaterialRecord {
  content: string;
}

export interface ContributionPreview {
  course_id: string;
  proposed_source_id: string;
  proposed_repo_path?: string | null;
  normalized_content: string;
  has_h1_title: boolean;
  question_marker_count: number;
  warnings: string[];
}

export interface ContributionRecord {
  contribution_id: string;
  user_id: string;
  material_id: string | null;
  course_id: string;
  proposed_source_id: string;
  proposed_repo_path?: string;
  title: string;
  state: ContributionState;
  pr_url: string | null;
  maintainer_note: string | null;
  char_count: number;
  created_at: string;
  updated_at: string;
  expires_at: string;
  mock_only: boolean;
}

export interface ContributionConfirmations {
  course_confirmed: boolean;
  source_confirmed: boolean;
  public_share_rights_confirmed: boolean;
  no_sensitive_info_confirmed: boolean;
  public_pr_visibility_acknowledged: boolean;
}
