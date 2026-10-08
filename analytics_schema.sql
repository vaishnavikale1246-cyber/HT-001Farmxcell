-- AgriHelper farmer analytics: additive schema only.
-- Existing users, crops, fertilizers, loans and calendar tables are unchanged.

CREATE TABLE IF NOT EXISTS disease_detection_history (
    detection_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    crop_id INTEGER REFERENCES crops(crop_id) ON DELETE SET NULL,
    predicted_crop VARCHAR(120) NOT NULL,
    predicted_disease VARCHAR(180) NOT NULL,
    image_filename VARCHAR(255),
    confidence NUMERIC(5,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS farmer_activity (
    activity_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(40) NOT NULL,
    crop_id INTEGER REFERENCES crops(crop_id) ON DELETE SET NULL,
    fertilizer_id INTEGER REFERENCES fertilizers(fertilizer_id) ON DELETE SET NULL,
    loan_id INTEGER REFERENCES loans(loan_id) ON DELETE SET NULL,
    detection_id BIGINT REFERENCES disease_detection_history(detection_id) ON DELETE SET NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_farmer_activity_created_at
    ON farmer_activity(created_at);
CREATE INDEX IF NOT EXISTS idx_farmer_activity_type
    ON farmer_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_farmer_activity_user
    ON farmer_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_farmer_activity_crop
    ON farmer_activity(crop_id);
CREATE INDEX IF NOT EXISTS idx_farmer_activity_fertilizer
    ON farmer_activity(fertilizer_id);
CREATE INDEX IF NOT EXISTS idx_detection_history_created_at
    ON disease_detection_history(created_at);
CREATE INDEX IF NOT EXISTS idx_detection_history_crop
    ON disease_detection_history(crop_id, predicted_crop);
CREATE INDEX IF NOT EXISTS idx_detection_history_disease
    ON disease_detection_history(predicted_disease);
