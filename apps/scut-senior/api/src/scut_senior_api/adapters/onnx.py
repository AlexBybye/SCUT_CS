"""CPU-only ONNX embedding adapter for ``bge-small-zh-v1.5``.

The model directory is supplied by configuration and must contain an ONNX
graph (``model.onnx``) plus a Hugging Face ``tokenizer.json``.  Imports are
lazy so the default lexical-only runtime does not require ML dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..embedding import EmbeddingProvider


DEFAULT_ONNX_MODEL_ID = "bge-small-zh-v1.5"
DEFAULT_ONNX_DIMENSIONS = 512


class OnnxEmbeddingProvider:
    """Mean-pool and L2-normalize BGE ONNX outputs on the CPU."""

    def __init__(
        self,
        model_dir: Path,
        *,
        model_id: str = DEFAULT_ONNX_MODEL_ID,
        dimensions: int = DEFAULT_ONNX_DIMENSIONS,
        max_length: int = 512,
    ) -> None:
        if not isinstance(model_dir, Path):
            raise TypeError("ONNX model_dir must be a Path")
        if not model_id or not isinstance(model_id, str):
            raise ValueError("ONNX embedding model_id must be a non-empty string")
        if isinstance(dimensions, bool) or not isinstance(dimensions, int) or dimensions < 1:
            raise ValueError("embedding dimensions must be a positive integer")
        if isinstance(max_length, bool) or not isinstance(max_length, int) or max_length < 8:
            raise ValueError("ONNX max_length must be an integer >= 8")
        model_root = model_dir.resolve()
        model_path = model_root / "model.onnx"
        tokenizer_path = model_root / "tokenizer.json"
        if not model_path.is_file() or not tokenizer_path.is_file():
            raise FileNotFoundError(
                "ONNX embedding model directory must contain model.onnx and tokenizer.json"
            )
        try:
            import numpy as np
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as exc:  # pragma: no cover - exercised in deployment env
            raise RuntimeError(
                "ONNX embedding requires the 'onnx' optional dependencies "
                "(onnxruntime and tokenizers)"
            ) from exc

        self.model_id = model_id
        self.dimensions = dimensions
        self._np = np
        self._tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self._session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self._input_names = {item.name for item in self._session.get_inputs()}
        self._max_length = max_length

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        encoded = self._tokenizer.encode_batch([str(text) for text in texts])
        encoded = [
            item
            for item in encoded
        ]
        max_len = min(
            self._max_length,
            max(len(item.ids) for item in encoded),
        )
        input_ids = self._np.zeros((len(encoded), max_len), dtype=self._np.int64)
        attention_mask = self._np.zeros_like(input_ids)
        token_type_ids = self._np.zeros_like(input_ids)
        for row, item in enumerate(encoded):
            length = min(max_len, len(item.ids))
            input_ids[row, :length] = item.ids[:length]
            attention_mask[row, :length] = 1
            if item.type_ids:
                token_type_ids[row, :length] = item.type_ids[:length]
        inputs = {
            name: value
            for name, value in (
                ("input_ids", input_ids),
                ("attention_mask", attention_mask),
                ("token_type_ids", token_type_ids),
            )
            if name in self._input_names
        }
        outputs = self._session.run(None, inputs)
        hidden = next(
            (value for value in outputs if getattr(value, "ndim", 0) == 3),
            None,
        )
        if hidden is None or hidden.shape[0] != len(texts) or hidden.shape[2] != self.dimensions:
            raise RuntimeError("ONNX embedding output has an unexpected shape")
        mask = attention_mask.astype(self._np.float32)[..., None]
        pooled = (hidden * mask).sum(axis=1) / self._np.maximum(mask.sum(axis=1), 1e-9)
        norms = self._np.linalg.norm(pooled, axis=1, keepdims=True)
        normalized = pooled / self._np.maximum(norms, 1e-12)
        return normalized.astype(self._np.float32).tolist()
