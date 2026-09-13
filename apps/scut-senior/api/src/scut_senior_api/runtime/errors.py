"""Runtime-specific errors that retain the service's public API semantics."""

from __future__ import annotations


class ContractConflict(ValueError):
    """A valid request or dependency result violates a workflow invariant."""
