from __future__ import annotations

from .auth import AuthRequired, AuthenticatedPrincipal
from .byok_catalog import (
    ByokProviderCatalog,
    ByokProviderDisabled,
    ByokProviderNotRegistered,
)
from .contracts import ModelCredentialStatus, ModelCredentialUpsert
from .credentials import (
    CredentialCipher,
    CredentialDecryptionError,
    EncryptedCredential,
    validate_user_api_key,
)
from .ports import ModelCredentialRepository, StoredModelCredential


MASKED_MODEL_KEY = "••••••••"


class ModelCredentialError(RuntimeError):
    def __init__(self, *, status_code: int, code: str, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


class ModelCredentialManager:
    """Owns session-bound credential validation, AEAD, and safe public metadata."""

    def __init__(
        self,
        *,
        repository: ModelCredentialRepository,
        catalog: ByokProviderCatalog,
        cipher: CredentialCipher | None,
    ):
        self._repository = repository
        self._catalog = catalog
        self._cipher = cipher

    def list_statuses(
        self, principal: AuthenticatedPrincipal
    ) -> list[ModelCredentialStatus]:
        self._require_active_session(principal)
        session_active = self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        )
        configured = {
            record.provider_id: record
            for record in self._repository.list_model_credentials(principal.user_id)
        }
        return [
            self._status(
                entry.provider_id.value,
                configured.get(entry.provider_id.value),
                session_active,
            )
            for entry in self._catalog.entries
        ]

    def replace(
        self,
        principal: AuthenticatedPrincipal,
        provider_id: str,
        payload: ModelCredentialUpsert,
    ) -> ModelCredentialStatus:
        entry = self._require_enabled_provider(provider_id)
        cipher = self._cipher
        if cipher is None:
            raise ModelCredentialError(
                status_code=503,
                code="byok_encryption_unavailable",
                detail="用户 API Key 加密服务未配置，当前无法保存凭据。",
            )
        self._require_active_session(principal)
        api_key = payload.api_key.get_secret_value()
        try:
            validate_user_api_key(api_key)
        except ValueError:
            raise ModelCredentialError(
                status_code=422,
                code="invalid_model_credential",
                detail="API Key 格式无效。",
            ) from None
        encrypted = cipher.encrypt(
            api_key,
            user_id=principal.user_id,
            provider_id=provider_id,
        )
        record = self._repository.upsert_model_credential(
            user_id=principal.user_id,
            provider_id=provider_id,
            ciphertext=encrypted.ciphertext,
            nonce=encrypted.nonce,
            algorithm=encrypted.algorithm,
            key_version=encrypted.key_version,
        )
        # The credential is scoped to the user, not the session, so it persists
        # across re-login on another device. The active-session check above is
        # what authorizes this write.
        return self._status(entry.provider_id.value, record, True)

    def delete(
        self, principal: AuthenticatedPrincipal, provider_id: str
    ) -> None:
        self._resolve_provider(provider_id)
        self._require_active_session(principal)
        deleted = self._repository.delete_model_credential(
            principal.user_id, provider_id
        )
        if not deleted and not self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        ):
            raise AuthRequired()

    def load_api_key(
        self, principal: AuthenticatedPrincipal, provider_id: str
    ) -> str:
        self._require_enabled_provider(provider_id)
        cipher = self._cipher
        if cipher is None:
            raise ModelCredentialError(
                status_code=503,
                code="byok_encryption_unavailable",
                detail="用户 API Key 加密服务未配置。",
            )
        record = self._repository.get_model_credential(
            principal.user_id, provider_id
        )
        if record is None:
            if not self._repository.session_is_active(
                principal.user_id, principal.auth_session_id
            ):
                raise AuthRequired()
            raise ModelCredentialError(
                status_code=409,
                code="model_credential_not_configured",
                detail="当前账号尚未保存该供应商的 API Key。",
            )
        try:
            api_key = cipher.decrypt(
                EncryptedCredential(
                    ciphertext=record.ciphertext,
                    nonce=record.nonce,
                    key_version=record.key_version,
                    algorithm=record.algorithm,
                ),
                user_id=principal.user_id,
                provider_id=provider_id,
            )
        except CredentialDecryptionError:
            raise ModelCredentialError(
                status_code=503,
                code="model_credential_unavailable",
                detail="已保存的 API Key 无法解密，请删除后重新保存。",
            ) from None
        # Revalidate immediately before the caller is allowed to submit the
        # provider request. Logout/revoke/expiry therefore invalidates late work.
        self._require_active_session(principal)
        return api_key

    def _require_active_session(self, principal: AuthenticatedPrincipal) -> None:
        if principal.is_mock or not self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        ):
            raise AuthRequired()

    def _resolve_provider(self, provider_id: str):
        try:
            return self._catalog.resolve_provider(provider_id)
        except ByokProviderNotRegistered:
            raise ModelCredentialError(
                status_code=422,
                code="byok_provider_not_registered",
                detail="该 BYOK 供应商未登记。",
            ) from None

    def _require_enabled_provider(self, provider_id: str):
        try:
            return self._catalog.require_enabled(provider_id)
        except ByokProviderNotRegistered:
            raise ModelCredentialError(
                status_code=422,
                code="byok_provider_not_registered",
                detail="该 BYOK 供应商未登记。",
            ) from None
        except ByokProviderDisabled:
            raise ModelCredentialError(
                status_code=503,
                code="byok_provider_disabled",
                detail="该 BYOK 供应商当前未启用。",
            ) from None

    def _status(
        self,
        provider_id: str,
        record: StoredModelCredential | None,
        session_active: bool,
    ) -> ModelCredentialStatus:
        entry = self._catalog.resolve_provider(provider_id)
        model_id = entry.models[0].model_id
        if record is None:
            return ModelCredentialStatus(
                provider_id=provider_id,
                model_id=model_id,
                configured=False,
                masked_key=None,
                expires_at=None,
                writable=False,
                source="user_key",
                updated_at=None,
            )
        return ModelCredentialStatus(
            provider_id=provider_id,
            model_id=model_id,
            configured=True,
            masked_key=MASKED_MODEL_KEY,
            expires_at=record.expires_at,
            writable=self._cipher is not None and session_active,
            source="user_key",
            updated_at=record.updated_at,
        )
