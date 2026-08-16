from __future__ import annotations

from dataclasses import dataclass, field
from os import urandom
from uuid import UUID

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


AES_256_KEY_BYTES = 32
AES_GCM_NONCE_BYTES = 12
CREDENTIAL_ALGORITHM = "AES-256-GCM"


class CredentialDecryptionError(RuntimeError):
    """Safe failure for a wrong key version, AAD binding, or modified ciphertext."""


@dataclass(frozen=True, slots=True)
class EncryptedCredential:
    ciphertext: bytes = field(repr=False)
    nonce: bytes = field(repr=False)
    key_version: int
    algorithm: str = CREDENTIAL_ALGORITHM


class CredentialCipher:
    """AES-256-GCM bound to one user, login session, and provider."""

    def __init__(self, master_key: bytes, key_version: int):
        if len(master_key) != AES_256_KEY_BYTES:
            raise ValueError("credential master key must contain exactly 32 bytes")
        if isinstance(key_version, bool) or key_version < 1:
            raise ValueError("credential key version must be a positive integer")
        self._aead = AESGCM(master_key)
        self.key_version = key_version

    def encrypt(
        self,
        plaintext: str,
        *,
        user_id: UUID,
        auth_session_id: UUID,
        provider_id: str,
    ) -> EncryptedCredential:
        if not plaintext:
            raise ValueError("credential plaintext must not be empty")
        nonce = urandom(AES_GCM_NONCE_BYTES)
        ciphertext = self._aead.encrypt(
            nonce,
            plaintext.encode("utf-8"),
            _credential_aad(user_id, auth_session_id, provider_id),
        )
        return EncryptedCredential(ciphertext, nonce, self.key_version)

    def decrypt(
        self,
        encrypted: EncryptedCredential,
        *,
        user_id: UUID,
        auth_session_id: UUID,
        provider_id: str,
    ) -> str:
        if encrypted.key_version != self.key_version:
            raise CredentialDecryptionError("credential key version is unavailable")
        if encrypted.algorithm != CREDENTIAL_ALGORITHM:
            raise CredentialDecryptionError("credential algorithm is unavailable")
        if len(encrypted.nonce) != AES_GCM_NONCE_BYTES:
            raise CredentialDecryptionError("credential envelope is invalid")
        try:
            plaintext = self._aead.decrypt(
                encrypted.nonce,
                encrypted.ciphertext,
                _credential_aad(user_id, auth_session_id, provider_id),
            )
            decoded = plaintext.decode("utf-8")
        except (InvalidTag, UnicodeDecodeError):
            raise CredentialDecryptionError(
                "credential authentication failed"
            ) from None
        if not decoded:
            raise CredentialDecryptionError("credential plaintext is invalid")
        return decoded


def _credential_aad(
    user_id: UUID, auth_session_id: UUID, provider_id: str
) -> bytes:
    if not provider_id or "\x1f" in provider_id:
        raise ValueError("provider_id is invalid for credential AAD")
    return (
        f"scut-senior-byok-v1\x1f{user_id}\x1f{auth_session_id}\x1f{provider_id}"
    ).encode("utf-8")
