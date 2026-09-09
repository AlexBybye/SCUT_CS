import type {
  ByokCredentialStatus,
  ModelCatalog,
  ModelCatalogItem,
} from "./contracts";

type ModelIdentity = Pick<
  ModelCatalogItem,
  "model_source" | "provider_id" | "model_id"
>;

export function modelKey(model: ModelIdentity): string {
  return `${model.model_source}:${model.provider_id}:${model.model_id}`;
}

export function modelsForRuntime(
  catalog: Pick<ModelCatalog, "platform_credential_configured">,
  models: readonly ModelCatalogItem[],
  mockModel: ModelCatalogItem,
  allowMockPath: boolean,
): ModelCatalogItem[] {
  const hasMockPath = models.some(
    (model) =>
      model.provider_id === mockModel.provider_id &&
      model.model_id === mockModel.model_id &&
      model.model_source === mockModel.model_source,
  );
  if (allowMockPath && !catalog.platform_credential_configured && !hasMockPath) {
    return [...models, mockModel];
  }
  return [...models];
}

export function initialModelSelectionKey(
  catalog: Pick<ModelCatalog, "real_platform_default_available">,
  models: readonly ModelCatalogItem[],
  mockModel: ModelIdentity,
): string {
  if (catalog.real_platform_default_available) return "";

  const selectableMock = models.find(
    (model) =>
      model.user_selectable &&
      model.provider_id === mockModel.provider_id &&
      model.model_id === mockModel.model_id &&
      model.model_source === mockModel.model_source,
  );
  return selectableMock ? modelKey(selectableMock) : "";
}

export function configuredByokModelOptions(
  statuses: readonly ByokCredentialStatus[],
): ModelCatalogItem[] {
  return statuses.map((status) => ({
        provider_id: status.provider_id,
        model_id: status.model_id,
        company: status.display_name,
        display_name: status.model_id,
        model_source: "user_key" as const,
        billing_label: "user_key",
        availability_status: "available",
        context_length: 0,
        input_modalities: ["text"],
        supports_structured_outputs: true,
        is_preview: false,
        user_selectable: true,
        last_checked_at: null,
      }));
}
