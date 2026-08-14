from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .paths import CONTRACT_ROOT


class UnknownCourseError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CourseRecord:
    course_id: str
    display_name: str
    aliases: tuple[str, ...]
    repository_paths: tuple[str, ...]
    is_open: bool
    fixture_available: bool


class CourseRegistry:
    def __init__(self, records: list[CourseRecord], contract_version: str = "v1"):
        self.records = tuple(records)
        self.contract_version = contract_version
        self._by_id = {record.course_id: record for record in records}
        self._by_alias: dict[str, CourseRecord] = {}
        for record in records:
            candidates = (record.course_id, record.display_name, *record.aliases)
            for candidate in candidates:
                key = normalize_course_name(candidate)
                previous = self._by_alias.get(key)
                if previous is not None and previous.course_id != record.course_id:
                    raise ValueError(
                        f"duplicate normalized course alias {candidate!r}: "
                        f"{previous.course_id} vs {record.course_id}"
                    )
                self._by_alias[key] = record

    @classmethod
    def load(cls, path: Path | None = None) -> "CourseRegistry":
        registry_path = path or CONTRACT_ROOT / "courses.json"
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        records = [
            CourseRecord(
                course_id=item["course_id"],
                display_name=item["display_name"],
                aliases=tuple(item.get("aliases", [])),
                repository_paths=tuple(item.get("repository_paths", [])),
                is_open=bool(item["is_open"]),
                fixture_available=bool(item.get("fixture_available", False)),
            )
            for item in payload["courses"]
        ]
        return cls(records, contract_version=payload["contract_version"])

    def resolve(self, course_id_or_alias: str) -> CourseRecord:
        direct = self._by_id.get(course_id_or_alias)
        if direct is not None:
            return direct
        record = self._by_alias.get(normalize_course_name(course_id_or_alias))
        if record is None:
            raise UnknownCourseError(f"unknown course: {course_id_or_alias}")
        return record

    def get(self, course_id: str) -> CourseRecord:
        try:
            return self._by_id[course_id]
        except KeyError as exc:
            raise UnknownCourseError(f"unknown course_id: {course_id}") from exc


def normalize_course_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(normalized.split())
