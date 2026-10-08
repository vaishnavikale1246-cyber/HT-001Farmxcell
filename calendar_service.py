"""Build read-only, preplanned agricultural calendars from verified profiles."""

from calendar import monthrange
from datetime import date, timedelta

from translation_service import apply_record_translations, fetch_translation_map


MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def _recommended_sowing_date(year, sowing_months):
    """Use the first configured month; farmers never enter dates manually."""
    month = min(sowing_months)
    return date(year, month, 15)


def _date_status(start_date, end_date, today):
    if end_date < today:
        return "completed"
    if start_date <= today <= end_date:
        return "current"
    return "upcoming"


def _months_touched(start_date, end_date, plan_year):
    """Return each month in plan_year touched by an activity date range."""
    cursor = date(max(start_date.year, plan_year), 1, 1)
    if start_date.year == plan_year:
        cursor = date(plan_year, start_date.month, 1)

    last = min(end_date, date(plan_year, 12, 31))
    result = []
    while cursor <= last and cursor.year == plan_year:
        result.append(cursor.month)
        if cursor.month == 12:
            break
        cursor = date(plan_year, cursor.month + 1, 1)
    return result


def list_calendar_crops(db_cursor, plan_year=None, language='en'):
    plan_year = plan_year or date.today().year
    db_cursor.execute(
        """
        SELECT c.crop_id, c.name, c.category, c.season, c.duration,
               p.sowing_months, p.region, p.duration_days
        FROM crops c
        JOIN crop_calendar_profiles p ON p.crop_id = c.crop_id
        WHERE p.is_active = TRUE
        ORDER BY c.name
        """
    )

    crops = []
    for row in db_cursor.fetchall():
        sowing_date = _recommended_sowing_date(plan_year, row[5])
        crops.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "season": row[3],
            "databaseDuration": row[4],
            "sowingMonths": list(row[5]),
            "recommendedSowingDate": sowing_date.isoformat(),
            "region": row[6],
            "durationDays": row[7],
        })
    return apply_record_translations(
        db_cursor,
        'crop',
        crops,
        language,
        {
            'name': 'name',
            'category': 'category',
            'season': 'season',
            'duration': 'databaseDuration',
        },
    )


def crops_to_plant_this_month(db_cursor, month, language='en'):
    db_cursor.execute(
        """
        SELECT c.crop_id, c.name, c.season, p.region
        FROM crops c
        JOIN crop_calendar_profiles p ON p.crop_id = c.crop_id
        WHERE p.is_active = TRUE AND %s = ANY(p.sowing_months)
        ORDER BY c.name
        """,
        (month,),
    )
    crops = [
        {"id": row[0], "name": row[1], "season": row[2], "region": row[3]}
        for row in db_cursor.fetchall()
    ]
    return apply_record_translations(
        db_cursor,
        'crop',
        crops,
        language,
        {'name': 'name', 'season': 'season'},
    )


def build_crop_calendar(db_cursor, crop_id, plan_year, language='en'):
    db_cursor.execute(
        """
        SELECT p.profile_id, c.crop_id, c.name, c.category, c.season,
               c.duration, p.sowing_months, p.duration_days,
               p.harvest_window_days, p.region, p.source_name,
               p.source_url, p.last_verified
        FROM crop_calendar_profiles p
        JOIN crops c ON c.crop_id = p.crop_id
        WHERE c.crop_id = %s AND p.is_active = TRUE
        """,
        (crop_id,),
    )
    profile = db_cursor.fetchone()
    if not profile:
        return None

    profile_id = profile[0]
    sowing_months = list(profile[6])
    today = date.today()

    db_cursor.execute(
        """
        SELECT activity_id, activity_type, growth_stage, start_day, end_day, title,
               guidance, priority, source_name, source_url
        FROM farming_activities
        WHERE profile_id = %s
        ORDER BY start_day, activity_id
        """,
        (profile_id,),
    )
    activity_rows = db_cursor.fetchall()

    db_cursor.execute(
        """
        SELECT risk_id, disease_name, start_day, end_day, risk_level,
               trigger_conditions, symptoms, precautions,
               monitoring_frequency, source_name, source_url
        FROM crop_disease_risks
        WHERE profile_id = %s
        ORDER BY start_day, risk_id
        """,
        (profile_id,),
    )
    risk_rows = db_cursor.fetchall()

    activity_translations = fetch_translation_map(
        db_cursor, 'calendar_activity', [row[0] for row in activity_rows], language
    )
    risk_translations = fetch_translation_map(
        db_cursor, 'calendar_risk', [row[0] for row in risk_rows], language
    )
    profile_translations = fetch_translation_map(
        db_cursor, 'calendar_profile', [profile_id], language
    )
    crop = apply_record_translations(
        db_cursor,
        'crop',
        [{
            "id": profile[1],
            "name": profile[2],
            "category": profile[3],
            "season": profile[4],
            "databaseDuration": profile[5],
        }],
        language,
        {
            'name': 'name',
            'category': 'category',
            'season': 'season',
            'duration': 'databaseDuration',
        },
    )[0]

    def translated(translations, entity_id, field_name, fallback):
        return translations.get((entity_id, field_name)) or fallback

    months = [
        {
            "number": month,
            "name": MONTH_NAMES[month - 1],
            "activities": [],
            "risks": [],
        }
        for month in range(1, 13)
    ]

    # The previous and current sowing cycles ensure a Jan-Dec view is complete
    # for crops such as wheat that cross the calendar-year boundary.
    cycles = []
    for cycle_year in (plan_year - 1, plan_year):
        sowing_date = _recommended_sowing_date(cycle_year, sowing_months)
        harvest_start = sowing_date + timedelta(days=profile[7])
        harvest_end = harvest_start + timedelta(days=profile[8])
        cycles.append({
            "season": f"{cycle_year}/{str(cycle_year + 1)[-2:]}",
            "sowingDate": sowing_date.isoformat(),
            "harvestWindow": {
                "start": harvest_start.isoformat(),
                "end": harvest_end.isoformat(),
            },
        })

        for row in activity_rows:
            start = sowing_date + timedelta(days=row[3])
            end = sowing_date + timedelta(days=row[4])
            if end.year < plan_year or start.year > plan_year:
                continue
            item = {
                "type": translated(activity_translations, row[0], 'activity_type', row[1]),
                "stage": translated(activity_translations, row[0], 'growth_stage', row[2]),
                "title": translated(activity_translations, row[0], 'title', row[5]),
                "guidance": translated(activity_translations, row[0], 'guidance', row[6]),
                "priority": row[7],
                "priorityLabel": translated(
                    activity_translations, row[0], 'priority', row[7]
                ),
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "status": _date_status(start, end, today),
                "cycle": f"{cycle_year}/{str(cycle_year + 1)[-2:]}",
                "source": {
                    "type": "verified_reference",
                    "name": row[8],
                    "url": row[9],
                },
            }
            for month in _months_touched(start, end, plan_year):
                months[month - 1]["activities"].append(item)

        for row in risk_rows:
            start = sowing_date + timedelta(days=row[2])
            end = sowing_date + timedelta(days=row[3])
            if end.year < plan_year or start.year > plan_year:
                continue
            translated_precautions = risk_translations.get((row[0], 'precautions'))
            precautions = (
                [
                    item.strip()
                    for item in translated_precautions.replace(';', '\n').splitlines()
                    if item.strip()
                ]
                if translated_precautions
                else list(row[7])
            )
            risk = {
                "disease": translated(risk_translations, row[0], 'disease_name', row[1]),
                "level": translated(risk_translations, row[0], 'risk_level', row[4]),
                "conditions": translated(risk_translations, row[0], 'trigger_conditions', row[5]),
                "symptoms": translated(risk_translations, row[0], 'symptoms', row[6]),
                "precautions": precautions,
                "monitoringFrequency": translated(
                    risk_translations, row[0], 'monitoring_frequency', row[8]
                ),
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "source": {
                    "type": "verified_reference",
                    "name": row[9],
                    "url": row[10],
                },
            }
            for month in _months_touched(start, end, plan_year):
                months[month - 1]["risks"].append(risk)

    return {
        "year": plan_year,
        "crop": crop,
        "profile": {
            "region": translated(profile_translations, profile_id, 'region', profile[9]),
            "durationDays": profile[7],
            "sowingMonths": sowing_months,
            "source": {
                "type": "verified_reference",
                "name": profile[10],
                "url": profile[11],
                "lastVerified": profile[12].isoformat() if profile[12] else None,
            },
        },
        "cycles": cycles,
        "months": months,
        "historicalComparison": {
            "available": False,
            "message": "Historical farm records are not available yet. No comparison has been generated.",
        },
        "disclaimer": (
            "This is a preplanned reference calendar. Local soil, variety, irrigation "
            "and extension-office advice take priority. Disease cards indicate monitoring "
            "risk and are not a diagnosis."
        ),
    }
