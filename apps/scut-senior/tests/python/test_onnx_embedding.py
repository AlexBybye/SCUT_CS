from pathlib import Path

import pytest

from scut_senior_api.adapters.onnx import OnnxEmbeddingProvider


def test_onnx_provider_requires_exported_model_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="model.onnx"):
        OnnxEmbeddingProvider(tmp_path)
