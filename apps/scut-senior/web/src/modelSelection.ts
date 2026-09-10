import type {
  ByokCredentialStatus,
  ByokProviderCatalogItem,
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
  providers: readonly ByokProviderCatalogItem[],
  statuses: readonly ByokCredentialStatus[],
): ModelCatalogItem[] {
  return providers.flatMap((provider) => {
    const model = provider.models[0];
    const credentialMatchesFixedModel = statuses.some(
      (status) =>
        status.configured &&
        status.provider_id === provider.provider_id &&
        status.model_id === model?.model_id,
    );
    if (!provider.enabled || !model || !credentialMatchesFixedModel) {
      return [];
    }
    return [
      {
        provider_id: provider.provider_id,
        model_id: model.model_id,
        company: provider.display_name,
        display_name: `${model.company} · ${model.display_name}`,
        model_source: "user_key" as const,
        billing_label: "user_key",
        availability_status: "available",
        context_length: 0,
        input_modalities: ["text"],
        supports_structured_outputs: true,
        is_preview: false,
        user_selectable: true,
        last_checked_at: null,
      },
    ];
  });
}
