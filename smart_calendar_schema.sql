-- Smart Agricultural Calendar: additive schema only.
-- Existing AgriHelper tables and columns are not modified.

CREATE TABLE IF NOT EXISTS crop_calendar_profiles (
    profile_id SERIAL PRIMARY KEY,
    crop_id INTEGER NOT NULL UNIQUE REFERENCES crops(crop_id) ON DELETE CASCADE,
    sowing_months SMALLINT[] NOT NULL,
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    harvest_window_days INTEGER NOT NULL DEFAULT 14 CHECK (harvest_window_days >= 0),
    region VARCHAR(160) NOT NULL DEFAULT 'India - general reference',
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    last_verified DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (array_length(sowing_months, 1) > 0)
);

CREATE TABLE IF NOT EXISTS farming_activities (
    activity_id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES crop_calendar_profiles(profile_id) ON DELETE CASCADE,
    activity_type VARCHAR(40) NOT NULL,
    growth_stage VARCHAR(80) NOT NULL,
    start_day INTEGER NOT NULL,
    end_day INTEGER NOT NULL,
    title VARCHAR(160) NOT NULL,
    guidance TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    CHECK (end_day >= start_day),
    UNIQUE (profile_id, activity_type, start_day, title)
);

CREATE TABLE IF NOT EXISTS crop_disease_risks (
    risk_id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES crop_calendar_profiles(profile_id) ON DELETE CASCADE,
    disease_name VARCHAR(160) NOT NULL,
    start_day INTEGER NOT NULL,
    end_day INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'monitor',
    trigger_conditions TEXT NOT NULL,
    symptoms TEXT NOT NULL,
    precautions TEXT[] NOT NULL,
    monitoring_frequency VARCHAR(120) NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    CHECK (end_day >= start_day),
    UNIQUE (profile_id, disease_name, start_day)
);

CREATE INDEX IF NOT EXISTS idx_calendar_activity_profile
    ON farming_activities(profile_id, start_day);
CREATE INDEX IF NOT EXISTS idx_calendar_risk_profile
    ON crop_disease_risks(profile_id, start_day);
