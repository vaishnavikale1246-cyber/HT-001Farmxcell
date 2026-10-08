"""Apply administrator-reviewed translations to API records."""


SUPPORTED_LANGUAGES = {'en', 'hi', 'mr'}

TRANSLATABLE_FIELDS = {
    'crop': {
        'name', 'category', 'season', 'duration', 'soil', 'ph_range',
        'temperature', 'rainfall', 'yield_per_acre', 'market_price',
        'estimated_profit',
    },
    'fertilizer': {'name', 'type', 'nutrients', 'dosage', 'description'},
    'loan': {
        'name', 'short_name', 'type', 'region', 'description', 'interest',
        'max_amount', 'benefits',
    },
    'calendar_profile': {'region'},
    'calendar_activity': {
        'activity_type', 'growth_stage', 'title', 'guidance', 'priority'
    },
    'calendar_risk': {
        'disease_name', 'risk_level', 'trigger_conditions', 'symptoms',
        'precautions', 'monitoring_frequency',
    },
}


def normalize_language(value):
    language = str(value or '').strip().lower()
    return language if language in SUPPORTED_LANGUAGES else 'en'


def fetch_translation_map(cursor, entity_type, entity_ids, language):
    language = normalize_language(language)
    identifiers = [int(value) for value in entity_ids if value is not None]
    if language == 'en' or not identifiers:
        return {}

    cursor.execute(
        """
        SELECT entity_id, field_name, translated_text
        FROM content_translations
        WHERE entity_type=%s AND language_code=%s AND reviewed=TRUE
              AND entity_id = ANY(%s)
        """,
        (entity_type, language, identifiers),
    )
    return {
        (row[0], row[1]): row[2]
        for row in cursor.fetchall()
    }


def apply_record_translations(cursor, entity_type, records, language, field_map):
    """Overlay translated database fields while retaining English fallbacks."""
    translations = fetch_translation_map(
        cursor,
        entity_type,
        [record.get('id') for record in records],
        language,
    )
    for record in records:
        for database_field, response_field in field_map.items():
            translated = translations.get((record.get('id'), database_field))
            if translated:
                record[response_field] = translated
    return records
