-- AgriHelper multilingual content: additive schema only.
-- Existing users and agricultural records are not deleted or rewritten.

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(5) NOT NULL DEFAULT 'en';

CREATE TABLE IF NOT EXISTS content_translations (
    translation_id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(30) NOT NULL,
    entity_id INTEGER NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    language_code VARCHAR(5) NOT NULL,
    translated_text TEXT NOT NULL,
    reviewed BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (entity_type IN (
        'crop', 'fertilizer', 'loan', 'calendar_profile',
        'calendar_activity', 'calendar_risk'
    )),
    CHECK (language_code IN ('hi', 'mr')),
    UNIQUE (entity_type, entity_id, field_name, language_code)
);

ALTER TABLE content_translations
    DROP CONSTRAINT IF EXISTS content_translations_entity_type_check;
ALTER TABLE content_translations
    ADD CONSTRAINT content_translations_entity_type_check
    CHECK (entity_type IN (
        'crop', 'fertilizer', 'loan', 'calendar_profile',
        'calendar_activity', 'calendar_risk'
    ));

CREATE INDEX IF NOT EXISTS idx_content_translations_lookup
    ON content_translations(entity_type, language_code, entity_id);
