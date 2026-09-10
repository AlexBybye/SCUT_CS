from __future__ import annotations

import ipaddress
import json
import re
from collections.abc import Mapping
from dataclasses import replace
from urllib.parse import urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request

import idna

from .auth import AuthRequired, AuthenticatedPrincipal
from .adapters.http_security import build_no_redirect_opener
from .byok_catalog import ByokProviderCatalog
from .contracts import (
    ByokModel,
    ModelCredentialDiscovery,
    ModelCredentialStatus,
    ModelCredentialUpsert,
)
from .credentials import (
    CredentialCipher,
    CredentialDecryptionError,
    EncryptedCredential,
    validate_user_api_key,
)
from .ports import ModelCredentialRepository, StoredByokModel, StoredModelCredential


MASKED_MODEL_KEY = "••••••••"
CONNECTION_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
MAX_DISCOVERY_RESPONSE_BYTES = 4 * 1024 * 1024


class ByokDiscoveryHttpClient:
    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> tuple[int, bytes]:
        request = Request(url, headers=dict(headers), method="GET")
        try:
            with build_no_redirect_opener().open(request, timeout=timeout_seconds) as response:
                body = response.read(MAX_DISCOVERY_RESPONSE_BYTES + 1)
                return response.status, body
        except HTTPError as exc:
            body = exc.read(MAX_DISCOVERY_RESPONSE_BYTES + 1)
            return exc.code, body
        except (OSError, URLError):
            raise ModelCredentialError(
                status_code=503,
                code="byok_discovery_unavailable",
                detail="无法连接模型供应商的模型目录。",
            ) from None

class ModelCredentialError(RuntimeError):
    def __init__(self, *, status_code: int, code: str, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


def normalize_connection_id(value: str) -> str:
    connection_id = value.strip()
    if len(connection_id) > 64 or CONNECTION_ID_PATTERN.fullmatch(connection_id) is None:
        raise ModelCredentialError(
            status_code=422,
            code="invalid_byok_connection_id",
            detail="连接 ID 只能使用小写字母、数字和连字符，并且必须以字母开头。",
        )
    return connection_id


def normalize_base_url(value: str) -> str:
    """Validate the server-side destination before any credential is stored.

    The hosted backend accepts HTTPS provider endpoints only. Redirects remain
    disabled by the shared HTTP transport, and obvious local/private targets
    are rejected so a saved API key cannot be sent to a loopback or metadata
    service by mistake.
    """

    raw = value.strip().rstrip("/")
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError:
        parsed = None
        port = None
    if (
        parsed is None
        or parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ModelCredentialError(
            status_code=422,
            code="invalid_byok_base_url",
            detail="API 地址必须是无账号、查询参数和片段的 HTTPS Base URL。",
        )
    hostname = parsed.hostname.casefold().rstrip(".")
    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
        raise ModelCredentialError(
            status_code=422,
            code="invalid_byok_base_url",
            detail="API 地址不能指向本机或内网主机。",
        )
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is None:
        try:
            hostname = idna.encode(
                hostname, uts46=True, std3_rules=True
            ).decode("ascii").casefold().rstrip(".")
        except (idna.IDNAError, UnicodeError):
            raise ModelCredentialError(
                status_code=422,
                code="invalid_byok_base_url",
                detail="API 地址包含无效的主机名。",
            ) from None
        if "." not in hostname:
            raise ModelCredentialError(
                status_code=422,
                code="invalid_byok_base_url",
                detail="API 地址必须使用完整的公网主机名。",
            )
        if hostname == "localhost" or hostname.endswith(
            (".localhost", ".local", ".internal")
        ):
            raise ModelCredentialError(
                status_code=422,
                code="invalid_byok_base_url",
                detail="API 地址不能指向本机或内网主机。",
            )
    if address is not None and not address.is_global:
        raise ModelCredentialError(
            status_code=422,
            code="invalid_byok_base_url",
            detail="API 地址不能指向本机或内网地址。",
        )
    host_for_netloc = (
        f"[{hostname}]"
        if address is not None and address.version == 6
        else hostname
    )
    netloc = host_for_netloc if port is None else f"{host_for_netloc}:{port}"
    return urlunsplit(("https", netloc, parsed.path.rstrip("/"), "", ""))


class ModelCredentialManager:
    """Own encrypted user-defined OpenAI-compatible model connections."""

    def __init__(
        self,
        *,
        repository: ModelCredentialRepository,
        catalog: ByokProviderCatalog,
        cipher: CredentialCipher | None,
        discovery_http_client: ByokDiscoveryHttpClient | None = None,
    ):
        self._repository = repository
        self._catalog = catalog
        self._cipher = cipher
        self._discovery_http_client = discovery_http_client or ByokDiscoveryHttpClient()

    def list_statuses(
        self, principal: AuthenticatedPrincipal
    ) -> list[ModelCredentialStatus]:
        self._require_active_session(principal)
        self._require_runtime()
        session_active = self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        )
        return [
            self._status(record, session_active)
            for record in self._repository.list_model_credentials(principal.user_id)
        ]

    def replace(
        self,
        principal: AuthenticatedPrincipal,
        provider_id: str,
        payload: ModelCredentialUpsert,
    ) -> ModelCredentialStatus:
        self._require_runtime()
        cipher = self._cipher
        if cipher is None:
            raise ModelCredentialError(
                status_code=503,
                code="byok_encryption_unavailable",
                detail="用户 API Key 加密服务未配置，当前无法保存凭据。",
            )
        self._require_active_session(principal)
        connection_id = normalize_connection_id(provider_id)
        display_name = payload.display_name.strip()
        model_id = payload.model_id.strip()
        if not display_name or not model_id or any(ord(char) < 32 for char in display_name + model_id):
            raise ModelCredentialError(
                status_code=422,
                code="invalid_byok_connection",
                detail="连接名称和模型 ID 不能为空或包含控制字符。",
            )
        base_url = normalize_base_url(payload.base_url)
        existing = self._repository.get_model_credential(
            principal.user_id, connection_id
        )
        api_key = payload.api_key.get_secret_value() if payload.api_key is not None else None
        if api_key is None:
            if existing is None:
                raise ModelCredentialError(
                    status_code=422,
                    code="byok_api_key_required",
                    detail="首次添加连接时必须提供 API Key。",
                )
            encrypted = EncryptedCredential(
                ciphertext=existing.ciphertext,
                nonce=existing.nonce,
                algorithm=existing.algorithm,
                key_version=existing.key_version,
            )
        else:
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
                provider_id=connection_id,
            )
        record = self._repository.upsert_model_credential(
            user_id=principal.user_id,
            provider_id=connection_id,
            display_name=display_name,
            base_url=base_url,
            model_id=model_id,
            protocol=payload.protocol,
            ciphertext=encrypted.ciphertext,
            nonce=encrypted.nonce,
            algorithm=encrypted.algorithm,
            key_version=encrypted.key_version,
            models=tuple(
                StoredByokModel(
                    model_id=model.model_id.strip(),
                    display_name=model.display_name.strip(),
                    context_length=model.context_length,
                    max_tokens=model.max_tokens,
                )
                for model in payload.models or ()
            ),
        )
        return self._status(record, True)

    def delete(
        self, principal: AuthenticatedPrincipal, provider_id: str
    ) -> None:
        self._require_runtime()
        connection_id = normalize_connection_id(provider_id)
        self._require_active_session(principal)
        deleted = self._repository.delete_model_credential(
            principal.user_id, connection_id
        )
        if not deleted and not self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        ):
            raise AuthRequired()

    def get_connection(
        self,
        principal: AuthenticatedPrincipal,
        provider_id: str,
        model_id: str,
    ) -> StoredModelCredential:
        self._require_runtime()
        connection_id = normalize_connection_id(provider_id)
        self._require_active_session(principal)
        record = self._repository.get_model_credential(
            principal.user_id, connection_id
        )
        if record is None:
            raise ModelCredentialError(
                status_code=409,
                code="model_credential_not_configured",
                detail="当前账号尚未保存该模型连接。",
            )
        model = next((item for item in record.models if item.model_id == model_id), None)
        if model is None and model_id != record.model_id:
            raise ModelCredentialError(
                status_code=422,
                code="byok_model_not_registered",
                detail="所选模型与已保存连接不一致。",
            )
        return record if model_id == record.model_id else replace(record, model_id=model_id)

    def discover(
        self,
        principal: AuthenticatedPrincipal,
        payload: ModelCredentialDiscovery,
    ) -> list[ByokModel]:
        self._require_runtime()
        self._require_active_session(principal)
        if payload.protocol != "openai_chat_completions":
            raise ModelCredentialError(
                status_code=422,
                code="byok_discovery_unsupported",
                detail="当前仅支持 OpenAI Chat Completions 的模型发现。",
            )
        base_url = normalize_base_url(payload.base_url)
        api_key = payload.api_key.get_secret_value() if payload.api_key is not None else None
        if api_key is not None:
            try:
                validate_user_api_key(api_key)
            except ValueError:
                raise ModelCredentialError(
                    status_code=422,
                    code="invalid_model_credential",
                    detail="API Key 格式无效。",
                ) from None
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        status_code, body = self._discovery_http_client.get_json(
            f"{base_url}/models", headers=headers, timeout_seconds=20.0
        )
        if len(body) > MAX_DISCOVERY_RESPONSE_BYTES:
            raise ModelCredentialError(
                status_code=422,
                code="byok_discovery_response_too_large",
                detail="模型目录响应过大，无法读取。",
            )
        if status_code < 200 or status_code >= 300:
            code = "byok_discovery_auth_failed" if status_code in {401, 403} else "byok_discovery_failed"
            detail = "模型供应商拒绝了模型目录请求，请检查 API Key。" if code.endswith("auth_failed") else "模型供应商暂时无法提供模型目录。"
            raise ModelCredentialError(status_code=422 if code.endswith("auth_failed") else 502, code=code, detail=detail)
        try:
            listing = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ModelCredentialError(
                status_code=502,
                code="byok_discovery_invalid_response",
                detail="模型供应商返回的模型目录不是有效 JSON。",
            ) from None
        rows: object
        if isinstance(listing, dict) and isinstance(listing.get("data"), list):
            rows = listing["data"]
        elif isinstance(listing, dict) and isinstance(listing.get("models"), dict):
            rows = [dict(value, id=key) for key, value in listing["models"].items() if isinstance(value, dict)]
        else:
            raise ModelCredentialError(
                status_code=502,
                code="byok_discovery_invalid_response",
                detail='模型目录必须包含 "data" 数组或 "models" 对象。',
            )
        models: list[ByokModel] = []
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            model_id = next((row.get(key) for key in ("id", "model_id") if isinstance(row.get(key), str) and row[key].strip()), None)
            if not isinstance(model_id, str):
                continue
            model_id = model_id.strip()[:100]
            if model_id in seen:
                continue
            seen.add(model_id)
            display_name = next((row.get(key) for key in ("name", "display_name", "displayName") if isinstance(row.get(key), str) and row[key].strip()), model_id)
            context = next((row.get(key) for key in ("context_length", "contextWindow", "context_window", "max_input_tokens") if isinstance(row.get(key), int) and row[key] >= 0), 0)
            output = next((row.get(key) for key in ("max_tokens", "max_output_tokens", "maxOutputTokens", "maxTokens") if isinstance(row.get(key), int) and row[key] > 0), None)
            models.append(ByokModel(model_id=model_id, display_name=str(display_name).strip()[:200], context_length=context, max_tokens=output))
        return models

    def load_api_key(
        self, principal: AuthenticatedPrincipal, provider_id: str
    ) -> str:
        self._require_runtime()
        cipher = self._cipher
        if cipher is None:
            raise ModelCredentialError(
                status_code=503,
                code="byok_encryption_unavailable",
                detail="用户 API Key 加密服务未配置。",
            )
        connection_id = normalize_connection_id(provider_id)
        record = self._repository.get_model_credential(
            principal.user_id, connection_id
        )
        if record is None:
            if not self._repository.session_is_active(
                principal.user_id, principal.auth_session_id
            ):
                raise AuthRequired()
            raise ModelCredentialError(
                status_code=409,
                code="model_credential_not_configured",
                detail="当前账号尚未保存该模型连接。",
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
                provider_id=connection_id,
            )
        except CredentialDecryptionError:
            raise ModelCredentialError(
                status_code=503,
                code="model_credential_unavailable",
                detail="已保存的 API Key 无法解密，请删除后重新保存。",
            ) from None
        self._require_active_session(principal)
        return api_key

    def _require_runtime(self) -> None:
        if not self._catalog.runtime_enabled:
            raise ModelCredentialError(
                status_code=503,
                code="byok_provider_disabled",
                detail="自定义模型连接当前未启用。",
            )

    def _require_active_session(self, principal: AuthenticatedPrincipal) -> None:
        if principal.is_mock or not self._repository.session_is_active(
            principal.user_id, principal.auth_session_id
        ):
            raise AuthRequired()

    def _status(
        self,
        record: StoredModelCredential,
        session_active: bool,
    ) -> ModelCredentialStatus:
        return ModelCredentialStatus(
            provider_id=record.provider_id,
            display_name=record.display_name,
            base_url=record.base_url,
            model_id=record.model_id,
            protocol="openai_chat_completions",
            configured=True,
            masked_key=MASKED_MODEL_KEY,
            expires_at=record.expires_at,
            writable=self._cipher is not None and session_active,
            source="user_key",
            updated_at=record.updated_at,
            models=[
                ByokModel(
                    model_id=model.model_id,
                    display_name=model.display_name,
                    context_length=model.context_length,
                    max_tokens=model.max_tokens,
                )
                for model in (record.models or (StoredByokModel(record.model_id, record.model_id),))
            ],
        )
