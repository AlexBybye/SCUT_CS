from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .contracts import (
    ConversationDetail,
    ModelCredentialStatusList,
    ModelCredentialUpsert,
    WorkflowResult,
    WorkflowRunRequest,
    WorkflowStreamEvent,
)
from .model_catalog import ModelCatalogResponse
from .paths import CONTRACT_ROOT


SCHEMA_MODELS = {
    "workflow-request.schema.json": WorkflowRunRequest,
    "workflow-result.schema.json": WorkflowResult,
    "workflow-stream-event.schema.json": WorkflowStreamEvent,
    "conversation-detail.schema.json": ConversationDetail,
    "model-catalog.schema.json": ModelCatalogResponse,
    "model-credential-list.schema.json": ModelCredentialStatusList,
    "model-credential-upsert.schema.json": ModelCredentialUpsert,
}

WORKFLOW_PAYLOAD_DEFS = {
    "knowledge_qa": "KnowledgeQaPayload",
    "exam_review": "ExamReviewPayload",
    "problem_tutor": "ProblemTutorPayload",
    "mistake_review": "MistakeReviewPayload",
    "temporary_material_reading": "TemporaryMaterialReadingPayload",
}


def render_schema_files() -> dict[str, str]:
    rendered: dict[str, str] = {}
    for filename, model in SCHEMA_MODELS.items():
        schema: dict[str, Any] = model.model_json_schema(mode="validation")
        if filename == "workflow-request.schema.json":
            _add_request_cross_field_invariants(schema)
        elif filename == "workflow-result.schema.json":
            _add_result_cross_field_invariants(schema)
        schema["$id"] = f"https://scut-senior.local/contracts/v1/{filename}"
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        rendered[filename] = (
            json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    return rendered


def _add_request_cross_field_invariants(schema: dict[str, Any]) -> None:
    """Encode Pydantic model-validator rules that JSON Schema cannot infer."""

    properties = schema["properties"]
    properties["attachments"]["maxItems"] = 0
    properties["allowed_course_ids"]["uniqueItems"] = True
    conditions: list[dict[str, Any]] = [
        {
            "if": {
                "properties": {"course_scope": {"const": "single"}},
                "required": ["course_scope"],
            },
            "then": {
                "properties": {
                    "course_id": {"type": "string", "minLength": 1},
                    "allowed_course_ids": {"maxItems": 0},
                },
                "required": ["course_id"],
            },
        },
        {
            "if": {
                "properties": {"course_scope": {"const": "cross"}},
                "required": ["course_scope"],
            },
            "then": {
                "properties": {
                    "course_id": {"type": "null"},
                    "allowed_course_ids": {"minItems": 2, "uniqueItems": True},
                }
            },
        },
    ]
    conditions.extend(
        {
            "if": {
                "properties": {"workflow_type": {"const": workflow_type}},
                "required": ["workflow_type"],
            },
            "then": {
                "properties": {
                    "workflow_payload": {"$ref": f"#/$defs/{payload_def}"}
                }
            },
        }
        for workflow_type, payload_def in WORKFLOW_PAYLOAD_DEFS.items()
    )
    schema["allOf"] = conditions


def _add_result_cross_field_invariants(schema: dict[str, Any]) -> None:
    """Keep the exported Citation locator rules aligned with Pydantic."""

    citation = schema["$defs"]["Citation"]
    citation["allOf"] = [
        {
            "if": {
                "properties": {"locator_type": {"const": "none"}},
                "required": ["locator_type"],
            },
            "then": {
                "properties": {
                    "locator_start": {"type": "null"},
                    "locator_end": {"type": "null"},
                    "question_id": {"type": "null"},
                    "heading_path": {"maxItems": 0},
                }
            },
        },
        {
            "if": {
                "properties": {"locator_type": {"enum": ["page", "slide"]}},
                "required": ["locator_type"],
            },
            "then": {
                "properties": {
                    "locator_start": {"type": "integer", "minimum": 1},
                    "locator_end": {
                        "anyOf": [
                            {"type": "integer", "minimum": 1},
                            {"type": "null"},
                        ]
                    },
                },
                "required": ["locator_start"],
            },
        },
        {
            "if": {
                "properties": {"locator_type": {"const": "heading"}},
                "required": ["locator_type"],
            },
            "then": {
                "anyOf": [
                    {
                        "properties": {
                            "locator_start": {"type": "string", "minLength": 1}
                        },
                        "required": ["locator_start"],
                    },
                    {
                        "properties": {"heading_path": {"minItems": 1}},
                        "required": ["heading_path"],
                    },
                ]
            },
        },
        {
            "if": {
                "properties": {"locator_type": {"const": "question"}},
                "required": ["locator_type"],
            },
            "then": {
                "anyOf": [
                    {
                        "properties": {
                            "locator_start": {"type": "string", "minLength": 1}
                        },
                        "required": ["locator_start"],
                    },
                    {
                        "properties": {
                            "question_id": {"type": "string", "minLength": 1}
                        },
                        "required": ["question_id"],
                    },
                ]
            },
        },
    ]

    external_resource = schema["$defs"]["ExternalResource"]
    external_resource["properties"]["url"] = {
        "type": "string",
        "format": "uri",
        "minLength": 1,
        "maxLength": 2083,
        "pattern": "^https://search\\.bilibili\\.com/all\\?keyword=[^&#]+$",
    }


def check_schema_files(schema_root: Path | None = None) -> list[str]:
    root = schema_root or CONTRACT_ROOT / "schemas"
    mismatches: list[str] = []
    for filename, expected in render_schema_files().items():
        path = root / filename
        if not path.is_file():
            mismatches.append(f"missing {path}")
        elif path.read_text(encoding="utf-8") != expected:
            mismatches.append(f"stale {path}")
    return mismatches


def write_schema_files(schema_root: Path | None = None) -> None:
    root = schema_root or CONTRACT_ROOT / "schemas"
    root.mkdir(parents=True, exist_ok=True)
    for filename, content in render_schema_files().items():
        (root / filename).write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export executable V1 API schemas")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_schema_files()
        return 0
    mismatches = check_schema_files()
    if mismatches:
        for mismatch in mismatches:
            print(mismatch)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
