"""Recording and aggregation helpers for AgriHelper's admin analytics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg2.extras import Json


ALLOWED_ACTIVITY_TYPES = {
    "login",
    "crop_view",
    "fertilizer_view",
    "disease_upload",
    "weather_view",
    "loan_view",
    "crop_search",
    "fertilizer_search",
    "calendar_view",
}


ACTIVITY_LABELS = {
    "login": "Logged in",
    "crop_view": "Viewed crop information",
    "fertilizer_view": "Viewed fertilizer information",
    "disease_upload": "Used AI disease detection",
    "weather_view": "Viewed weather",
    "loan_view": "Viewed loan information",
    "crop_search": "Searched crops",
    "fertilizer_search": "Searched fertilizers",
    "calendar_view": "Viewed smart calendar",
}

INDIA_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


def record_activity(
    cursor,
    user_id,
    activity_type,
    crop_id=None,
    fertilizer_id=None,
    loan_id=None,
    detection_id=None,
    details=None,
):
    if activity_type not in ALLOWED_ACTIVITY_TYPES:
        raise ValueError("Unsupported activity type")

    cursor.execute(
        """
        INSERT INTO farmer_activity
            (user_id, activity_type, crop_id, fertilizer_id, loan_id,
             detection_id, details)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING activity_id
        """,
        (
            user_id,
            activity_type,
            crop_id,
            fertilizer_id,
            loan_id,
            detection_id,
            Json(details or {}),
        ),
    )
    return cursor.fetchone()[0]


def record_disease_detection(
    cursor,
    user_id,
    predicted_crop,
    predicted_disease,
    confidence,
    image_filename,
):
    cursor.execute(
        "SELECT crop_id FROM crops WHERE LOWER(TRIM(name))=LOWER(TRIM(%s)) ORDER BY crop_id LIMIT 1",
        (predicted_crop,),
    )
    crop = cursor.fetchone()
    crop_id = crop[0] if crop else None

    cursor.execute(
        """
        INSERT INTO disease_detection_history
            (user_id, crop_id, predicted_crop, predicted_disease,
             image_filename, confidence)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING detection_id
        """,
        (
            user_id,
            crop_id,
            predicted_crop,
            predicted_disease,
            image_filename,
            round(float(confidence), 2),
        ),
    )
    detection_id = cursor.fetchone()[0]
    record_activity(
        cursor,
        user_id,
        "disease_upload",
        crop_id=crop_id,
        detection_id=detection_id,
    )
    return detection_id


def resolve_date_range(period):
    now = datetime.now(INDIA_TIMEZONE)
    if period == "7d":
        return now - timedelta(days=7), None
    if period == "30d":
        return now - timedelta(days=30), None
    if period == "year":
        return datetime(now.year, 1, 1, tzinfo=INDIA_TIMEZONE), None
    return None, None


def _activity_conditions(filters, alias="a"):
    conditions = []
    params = []
    start, end = resolve_date_range(filters.get("period"))
    if start:
        conditions.append(f"{alias}.created_at >= %s")
        params.append(start)
    if end:
        conditions.append(f"{alias}.created_at < %s")
        params.append(end)
    if filters.get("crop_id"):
        conditions.append(f"{alias}.crop_id = %s")
        params.append(filters["crop_id"])
    if filters.get("fertilizer_id"):
        conditions.append(f"{alias}.fertilizer_id = %s")
        params.append(filters["fertilizer_id"])
    if filters.get("activity_type"):
        conditions.append(f"{alias}.activity_type = %s")
        params.append(filters["activity_type"])
    if filters.get("disease"):
        conditions.append(
            f"EXISTS (SELECT 1 FROM disease_detection_history fd "
            f"WHERE fd.detection_id={alias}.detection_id AND fd.predicted_disease=%s)"
        )
        params.append(filters["disease"])
    return conditions, params


def _detection_conditions(filters, alias="d"):
    conditions = []
    params = []
    start, end = resolve_date_range(filters.get("period"))
    if start:
        conditions.append(f"{alias}.created_at >= %s")
        params.append(start)
    if end:
        conditions.append(f"{alias}.created_at < %s")
        params.append(end)
    if filters.get("crop_id"):
        conditions.append(
            f"({alias}.crop_id=%s OR LOWER({alias}.predicted_crop)="
            "(SELECT LOWER(name) FROM crops WHERE crop_id=%s))"
        )
        params.extend([filters["crop_id"], filters["crop_id"]])
    if filters.get("disease"):
        conditions.append(f"{alias}.predicted_disease = %s")
        params.append(filters["disease"])
    # A fertilizer filter or a non-disease activity filter has no matching
    # detection population, so disease charts should honestly be empty.
    if filters.get("fertilizer_id"):
        conditions.append("FALSE")
    if filters.get("activity_type") and filters["activity_type"] != "disease_upload":
        conditions.append("FALSE")
    return conditions, params


def _where(conditions):
    return " WHERE " + " AND ".join(conditions) if conditions else ""


def _number(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def _fetch_grouped(cursor, sql, params):
    cursor.execute(sql, params)
    return [{"label": row[0] or "Unknown", "value": _number(row[1])} for row in cursor.fetchall()]


def get_admin_analytics(cursor, filters):
    activity_conditions, activity_params = _activity_conditions(filters)
    detection_conditions, detection_params = _detection_conditions(filters)
    activity_where = _where(activity_conditions)
    detection_where = _where(detection_conditions)

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_farmers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crops")
    total_crops = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fertilizers")
    total_fertilizers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM loans")
    total_loans = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM farmer_activity a" + activity_where,
        activity_params,
    )
    total_activities = cursor.fetchone()[0]

    interest_conditions = activity_conditions + ["a.activity_type IN ('crop_view','calendar_view')", "a.crop_id IS NOT NULL"]
    cursor.execute(
        "SELECT COUNT(DISTINCT (a.user_id, a.crop_id)) FROM farmer_activity a" + _where(interest_conditions),
        activity_params,
    )
    crop_interests = cursor.fetchone()[0]

    fertilizer_conditions = activity_conditions + ["a.activity_type='fertilizer_view'"]
    cursor.execute(
        "SELECT COUNT(*) FROM farmer_activity a" + _where(fertilizer_conditions),
        activity_params,
    )
    fertilizer_interactions = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM disease_detection_history d" + detection_where,
        detection_params,
    )
    disease_uploads = cursor.fetchone()[0]

    crop_interest = _fetch_grouped(
        cursor,
        """
        SELECT c.name, COUNT(DISTINCT (a.user_id, a.crop_id))
        FROM farmer_activity a
        JOIN crops c ON c.crop_id=a.crop_id
        """ + _where(activity_conditions + ["a.activity_type IN ('crop_view','calendar_view')"]) +
        " GROUP BY c.crop_id, c.name ORDER BY 2 DESC, c.name LIMIT 10",
        activity_params,
    )

    disease_by_crop = _fetch_grouped(
        cursor,
        "SELECT d.predicted_crop, COUNT(*) FROM disease_detection_history d" + detection_where +
        " GROUP BY d.predicted_crop ORDER BY 2 DESC, d.predicted_crop LIMIT 10",
        detection_params,
    )

    disease_counts = _fetch_grouped(
        cursor,
        "SELECT d.predicted_disease, COUNT(*) FROM disease_detection_history d" + detection_where +
        " GROUP BY d.predicted_disease ORDER BY 2 DESC, d.predicted_disease LIMIT 10",
        detection_params,
    )

    cursor.execute(
        "SELECT d.predicted_disease, COUNT(*) FROM disease_detection_history d" +
        detection_where +
        " GROUP BY d.predicted_disease ORDER BY 2 ASC, d.predicted_disease LIMIT 1",
        detection_params,
    )
    lowest_disease_row = cursor.fetchone()

    fertilizer_counts = _fetch_grouped(
        cursor,
        """
        SELECT f.name, COUNT(*)
        FROM farmer_activity a
        JOIN fertilizers f ON f.fertilizer_id=a.fertilizer_id
        """ + _where(activity_conditions + ["a.activity_type='fertilizer_view'"]) +
        " GROUP BY f.fertilizer_id, f.name ORDER BY 2 DESC, f.name LIMIT 10",
        activity_params,
    )

    cursor.execute(
        """
        SELECT TO_CHAR(DATE_TRUNC('month', a.created_at), 'YYYY-MM'), COUNT(*)
        FROM farmer_activity a
        """ + activity_where +
        " GROUP BY DATE_TRUNC('month', a.created_at) ORDER BY DATE_TRUNC('month', a.created_at)",
        activity_params,
    )
    monthly = [{"label": row[0], "value": row[1]} for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT f.type, COUNT(*)
        FROM farmer_activity a
        JOIN fertilizers f ON f.fertilizer_id=a.fertilizer_id
        """ + _where(activity_conditions + ["a.activity_type='fertilizer_view'"]) +
        " GROUP BY f.type ORDER BY 2 DESC, f.type LIMIT 1",
        activity_params,
    )
    top_fertilizer_type_row = cursor.fetchone()

    cursor.execute(
        """
        SELECT c.crop_id, c.name,
               COUNT(*) FILTER (WHERE a.activity_type='crop_view') AS views,
               COUNT(DISTINCT a.user_id) FILTER (
                   WHERE a.activity_type IN ('crop_view','calendar_view')
               ) AS interested_farmers
        FROM crops c
        LEFT JOIN farmer_activity a ON a.crop_id=c.crop_id
        """ + _where(activity_conditions) +
        " GROUP BY c.crop_id, c.name ORDER BY views DESC, interested_farmers DESC, c.name",
        activity_params,
    )
    crop_rows = cursor.fetchall()

    detection_by_crop_name = {item[0].lower(): item[1] for item in _detection_rows(cursor, detection_where, detection_params)}
    top_crops = [
        {
            "id": row[0],
            "name": row[1],
            "views": row[2],
            "interestedFarmers": row[3],
            "diseaseUploads": detection_by_crop_name.get(row[1].lower(), 0),
        }
        for row in crop_rows
    ]
    top_crops = sorted(
        [
            crop for crop in top_crops
            if crop["views"] or crop["interestedFarmers"] or crop["diseaseUploads"]
        ],
        key=lambda crop: (
            crop["views"], crop["diseaseUploads"], crop["interestedFarmers"]
        ),
        reverse=True,
    )[:5]

    cursor.execute(
        """
        SELECT u.name, a.activity_type, c.name, f.name, l.name,
               d.predicted_crop, d.predicted_disease, a.created_at
        FROM farmer_activity a
        JOIN users u ON u.user_id=a.user_id
        LEFT JOIN crops c ON c.crop_id=a.crop_id
        LEFT JOIN fertilizers f ON f.fertilizer_id=a.fertilizer_id
        LEFT JOIN loans l ON l.loan_id=a.loan_id
        LEFT JOIN disease_detection_history d ON d.detection_id=a.detection_id
        """ + activity_where + " ORDER BY a.created_at DESC LIMIT 15",
        activity_params,
    )
    recent = []
    for row in cursor.fetchall():
        resource = row[2] or row[3] or row[4] or row[5] or row[6] or "General"
        recent.append({
            "farmer": row[0],
            "activityType": row[1],
            "activity": ACTIVITY_LABELS.get(row[1], row[1].replace("_", " ").title()),
            "resource": resource,
            "createdAt": row[7].isoformat(),
        })

    cursor.execute("SELECT crop_id, name FROM crops ORDER BY name")
    crop_options = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    cursor.execute("SELECT fertilizer_id, name FROM fertilizers ORDER BY name")
    fertilizer_options = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT predicted_disease FROM disease_detection_history ORDER BY predicted_disease")
    disease_options = [row[0] for row in cursor.fetchall()]

    return {
        "overview": {
            "totalFarmers": total_farmers,
            "totalCrops": total_crops,
            "totalFertilizers": total_fertilizers,
            "totalLoans": total_loans,
            "cropInterests": crop_interests,
            "diseaseUploads": disease_uploads,
            "fertilizerInteractions": fertilizer_interactions,
            "totalActivities": total_activities,
        },
        "charts": {
            "cropInterest": crop_interest,
            "diseaseByCrop": disease_by_crop,
            "diseaseCounts": disease_counts,
            "fertilizerCounts": fertilizer_counts,
            "monthlyActivity": monthly,
        },
        "insights": {
            "highestDisease": disease_counts[0]["label"] if disease_counts else None,
            "lowestDisease": lowest_disease_row[0] if lowest_disease_row else None,
            "topFertilizer": fertilizer_counts[0]["label"] if fertilizer_counts else None,
            "topFertilizerType": top_fertilizer_type_row[0] if top_fertilizer_type_row else None,
        },
        "topCrops": top_crops,
        "recentActivity": recent,
        "availableFilters": {
            "crops": crop_options,
            "fertilizers": fertilizer_options,
            "diseases": disease_options,
            "activityTypes": [
                {"value": key, "label": label}
                for key, label in ACTIVITY_LABELS.items()
            ],
        },
        "trackingNotice": (
            "Analytics contain activity recorded after tracking was enabled. "
            "Earlier usage cannot be reconstructed."
        ),
    }


def _detection_rows(cursor, where_clause, params):
    cursor.execute(
        "SELECT predicted_crop, COUNT(*) FROM disease_detection_history d" + where_clause +
        " GROUP BY predicted_crop",
        params,
    )
    return cursor.fetchall()
