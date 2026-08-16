import type { AuthUser } from "./contracts";

export function canManageByokCredentials(
  user: Pick<AuthUser, "is_mock"> | null | undefined,
): boolean {
  return Boolean(user && !user.is_mock);
}
