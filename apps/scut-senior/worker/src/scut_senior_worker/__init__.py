"""Deterministic worker utilities shared by the SCUT Senior application.

Import concrete utilities from :mod:`scut_senior_worker.corpus_validator` and
:mod:`scut_senior_worker.corpus_builder`.
Keeping package import side-effect free also makes the validator CLI safe to
execute with ``python -m``.
"""
