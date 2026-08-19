-- Course plugin load/unload state.
-- Absence of a row means the course plugin is loaded (default), matching the
-- registry's registered-course semantics; an explicit unload row is the only
-- way to disable a course plugin. The table is append-auditable metadata and
-- is not a second source of truth for corpus content or activation.
CREATE TABLE course_plugin_states (
    course_id TEXT PRIMARY KEY,
    loaded INTEGER NOT NULL DEFAULT 1 CHECK (loaded IN (0, 1)),
    updated_at TEXT NOT NULL,
    updated_by_user_id TEXT
);
