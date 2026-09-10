export const BYOK_CATALOG_VERSION = "byok-connections-v1";

export function isCurrentByokCatalogVersion(value: string): boolean {
  return value === BYOK_CATALOG_VERSION;
}
