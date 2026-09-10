-- DSH-style custom connections keep one encrypted key with a selectable model
-- catalog. Existing connections remain valid through the loader fallback to
-- their legacy model_id.

ALTER TABLE model_credentials
    ADD COLUMN models_json TEXT NOT NULL DEFAULT '[]'
    CHECK (json_valid(models_json));
