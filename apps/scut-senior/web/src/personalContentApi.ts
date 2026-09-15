import { apiRequest } from "./api";
import type { ContributionConfirmations, ContributionRecord, MaintainerContributionDetail } from "./contracts";
import type { ContentHandoff } from "./personalContentSession";

export interface PrivateKnowledgeRecord {
  knowledge_id: string;
  course_id: string;
  title: string | null;
  char_count: number;
  content_sha256: string;
  created_at: string;
  expires_at: string;
}
export interface PrivateKnowledgeDetail extends PrivateKnowledgeRecord { content: string }
export type PersonalContributionDetail = MaintainerContributionDetail & { github_email?: string };
export type PersonalContributionInput = Partial<Pick<ContentHandoff, "run_id" | "workflow_type" | "citation_metadata" | "corpus_metadata">> & {
  material_id?: string;
  content?: string;
  course_id: string;
  title: string;
  github_email: string;
  supplementary_text?: string;
  confirmations: ContributionConfirmations;
};
const privatePath = (id: string) => `/api/v1/private-knowledge/${encodeURIComponent(id)}`;
const contributionPath = (id: string) => `/api/v1/contributions/${encodeURIComponent(id)}`;

export function listPrivateKnowledge(courseId = "", offset = 0, limit = 30): Promise<PrivateKnowledgeRecord[]> {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (courseId) query.set("course_id", courseId);
  return apiRequest(`/api/v1/private-knowledge?${query}`);
}
export function getPrivateKnowledge(id: string): Promise<PrivateKnowledgeDetail> { return apiRequest(privatePath(id)); }
export function deletePrivateKnowledge(id: string): Promise<void> { return apiRequest(privatePath(id), { method: "DELETE" }); }
export function renewPrivateKnowledge(id: string): Promise<PrivateKnowledgeRecord> { return apiRequest(`${privatePath(id)}/renew`, { method: "POST" }); }
export function exportPrivateKnowledge(id: string): Promise<PrivateKnowledgeDetail> { return apiRequest(`${privatePath(id)}/export`); }
export function getPersonalContribution(id: string): Promise<PersonalContributionDetail> { return apiRequest(`${contributionPath(id)}/detail`); }
export function exportPersonalContribution(id: string): Promise<PersonalContributionDetail> { return apiRequest(`${contributionPath(id)}/export`); }
export function sendPersonalContribution(input: PersonalContributionInput): Promise<ContributionRecord> {
  return apiRequest("/api/v1/contributions", { method: "POST", body: JSON.stringify(input) });
}
