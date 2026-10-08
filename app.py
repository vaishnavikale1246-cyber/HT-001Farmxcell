from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory, flash, url_for
import psycopg2
import click
import hmac
import os
from pathlib import Path
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from calendar_service import build_crop_calendar, crops_to_plant_this_month, list_calendar_crops
from analytics_service import (
    ALLOWED_ACTIVITY_TYPES,
    get_admin_analytics,
    record_activity,
    record_disease_detection,
)
from translation_service import (
    SUPPORTED_LANGUAGES,
    TRANSLATABLE_FIELDS,
    apply_record_translations,
    normalize_language,
)
from fertilizer_translation_seed import seed_fertilizer_translations
from crop_translation_seed import seed_crop_translations
from loan_translation_seed import seed_loan_translations

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'secret123')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.permanent_session_lifetime = timedelta(days=30)

BASE_DIR = Path(__file__).resolve().parent
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_ADMIN_ACCOUNTS = 2

# ================= DB CONNECTION =================
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
DATABASE_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'AgriHelper'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'root'),
    'port': os.environ.get('DB_PORT', '5432'),
    'connect_timeout': 5,
}


class LazyDatabaseConnection:
    """Connect only when a database-backed route is actually requested."""

    def __init__(self):
        self.connection = None

    def get(self):
        if self.connection is None or self.connection.closed:
            self.connection = (
                psycopg2.connect(DATABASE_URL, connect_timeout=5)
                if DATABASE_URL
                else psycopg2.connect(**DATABASE_CONFIG)
            )
        return self.connection

    def cursor(self):
        return self.get().cursor()

    def commit(self):
        return self.get().commit()

    def rollback(self):
        return self.get().rollback()


conn = LazyDatabaseConnection()


@app.cli.command('check-db')
def check_database_connection():
    """Verify the configured PostgreSQL connection and show its database."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT current_database(), current_user,
                   current_setting('server_version'),
                   (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public')
        """)
        database_name, database_user, server_version, table_count = cur.fetchone()
    except psycopg2.Error as error:
        if conn.connection is not None and not conn.connection.closed:
            conn.connection.rollback()
        raise click.ClickException(f'PostgreSQL connection failed: {error}') from error

    click.echo(
        f'Connected to PostgreSQL {server_version}: '
        f'database={database_name}, user={database_user}, public_tables={table_count}'
    )


def selected_language():
    """Return the authenticated preference, with a safe English fallback."""
    return normalize_language(session.get('language'))


AUTH_MESSAGES = {
    'hi': {
        'select_language': 'कृपया समर्थित भाषा चुनें।',
        'complete_fields': 'कृपया पंजीकरण के सभी फ़ील्ड भरें।',
        'password_length': 'पासवर्ड में कम से कम 8 अक्षर होने चाहिए।',
        'duplicate': 'इस ईमेल का खाता पहले से मौजूद है। कृपया लॉगिन करें।',
        'register_unavailable': 'पंजीकरण अभी उपलब्ध नहीं है। कृपया फिर प्रयास करें।',
        'register_success': 'पंजीकरण सफल रहा। अब आप उपयोगकर्ता के रूप में लॉगिन कर सकते हैं।',
        'select_role': 'लॉगिन से पहले प्रशासक या उपयोगकर्ता चुनें।',
        'login_unavailable': 'लॉगिन अभी उपलब्ध नहीं है। कृपया फिर प्रयास करें।',
        'invalid_credentials': 'ईमेल, पासवर्ड या चुनी गई भूमिका गलत है।',
    },
    'mr': {
        'select_language': 'कृपया समर्थित भाषा निवडा.',
        'complete_fields': 'कृपया नोंदणीतील सर्व माहिती भरा.',
        'password_length': 'पासवर्डमध्ये किमान 8 अक्षरे असणे आवश्यक आहे.',
        'duplicate': 'या ईमेलचे खाते आधीपासून आहे. कृपया लॉगिन करा.',
        'register_unavailable': 'नोंदणी सध्या उपलब्ध नाही. कृपया पुन्हा प्रयत्न करा.',
        'register_success': 'नोंदणी यशस्वी झाली. आता तुम्ही वापरकर्ता म्हणून लॉगिन करू शकता.',
        'select_role': 'लॉगिन करण्यापूर्वी प्रशासक किंवा वापरकर्ता निवडा.',
        'login_unavailable': 'लॉगिन सध्या उपलब्ध नाही. कृपया पुन्हा प्रयत्न करा.',
        'invalid_credentials': 'ईमेल, पासवर्ड किंवा निवडलेली भूमिका चुकीची आहे.',
    },
}

AUTH_MESSAGES_EN = {
    'select_language': 'Please select a supported language.',
    'complete_fields': 'Please complete every registration field.',
    'password_length': 'Password must contain at least 8 characters.',
    'duplicate': 'An account with this email already exists. Please log in instead.',
    'register_unavailable': 'Registration is temporarily unavailable. Please try again.',
    'register_success': 'Registration successful. You can now log in as a User.',
    'select_role': 'Please select Admin or User before logging in.',
    'login_unavailable': 'Login is temporarily unavailable. Please try again.',
    'invalid_credentials': 'Email, password, or selected role is incorrect.',
}


def auth_message(key, language):
    return AUTH_MESSAGES.get(normalize_language(language), {}).get(
        key, AUTH_MESSAGES_EN[key]
    )


def current_user_id():
    """Return the authenticated account ID, upgrading older session cookies."""
    user_id = session.get('user_id')
    if user_id:
        return user_id

    username = session.get('user')
    role = session.get('role')
    if not username or role not in {'user', 'admin'}:
        return None

    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM users WHERE name=%s AND role=%s ORDER BY user_id",
        (username, role)
    )
    matches = cur.fetchall()
    if len(matches) == 1:
        session['user_id'] = matches[0][0]
        return matches[0][0]
    return None

# ================= HOME =================
@app.route('/')
def home():
    return render_template("login.html")


# Serve the SPA dashboard and its root-level assets through Flask.
@app.route('/app.html')
def app_dashboard():
    if session.get('role') == 'user':
        return render_template('app.html')
    if session.get('role') == 'admin':
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))


@app.route('/main.css')
def main_stylesheet():
    return send_from_directory(BASE_DIR, 'main.css')


@app.route('/js/<path:filename>')
def javascript_asset(filename):
    return send_from_directory(BASE_DIR / 'js', filename)


@app.route('/uploads/css/<path:filename>')
def uploaded_css(filename):
    return send_from_directory(BASE_DIR / 'uploads' / 'css', filename)

# ================= REGISTER =================
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    raw_language = request.form.get('language', '').strip().lower()
    if raw_language not in SUPPORTED_LANGUAGES:
        flash(auth_message('select_language', raw_language), 'error')
        return redirect(url_for('home'))
    language = raw_language

    if not name or not email or not password:
        flash(auth_message('complete_fields', language), 'error')
        return redirect(url_for('home'))

    if len(password) < 8:
        flash(auth_message('password_length', language), 'error')
        return redirect(url_for('home'))

    # Public registration never grants administrative privileges.
    role = 'user'
    password_hash = generate_password_hash(password)

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (name,email,password,role,preferred_language)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (name, email, password_hash, role, language)
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        flash(auth_message('duplicate', language), 'error')
        return redirect(url_for('home'))
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Registration could not be completed')
        flash(auth_message('register_unavailable', language), 'error')
        return redirect(url_for('home'))

    flash(auth_message('register_success', language), 'success')
    return redirect(url_for('home'))


def password_matches(stored_password, submitted_password):
    """Support hashed passwords and migrate older plain-text accounts safely."""
    if stored_password.startswith(('scrypt:', 'pbkdf2:')):
        return check_password_hash(stored_password, submitted_password)
    return hmac.compare_digest(stored_password, submitted_password)

# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    selected_role = request.form.get('role', '').strip().lower()
    login_language = normalize_language(request.form.get('language'))

    if selected_role not in {'admin', 'user'}:
        flash(auth_message('select_role', login_language), 'error')
        return redirect(url_for('home'))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_id, name, password, role, preferred_language
            FROM users WHERE LOWER(email)=LOWER(%s) AND role=%s
            """,
            (email, selected_role)
        )
        user = cur.fetchone()
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Login lookup failed')
        flash(auth_message('login_unavailable', login_language), 'error')
        return redirect(url_for('home'))

    if user and password_matches(user[2], password):
        session.clear()
        session['user_id'] = user[0]
        session['user'] = user[1]
        session['role'] = user[3].strip().lower()
        session['language'] = normalize_language(user[4])
        session.permanent = True

        # Upgrade legacy plain-text passwords after a successful login.
        if not user[2].startswith(('scrypt:', 'pbkdf2:')):
            cur.execute(
                "UPDATE users SET password=%s WHERE user_id=%s",
                (generate_password_hash(password), user[0])
            )
            conn.commit()

        if session['role'] == "admin":
            return redirect(url_for('dashboard'))

        # Login analytics are useful to the administrator, but analytics must
        # never prevent a farmer from signing in.
        try:
            record_activity(cur, user[0], 'login')
            conn.commit()
        except psycopg2.Error:
            conn.rollback()
            app.logger.exception('Farmer login activity could not be recorded')

        return redirect(url_for('user_dashboard'))

    flash(auth_message('invalid_credentials', login_language), 'error')
    return redirect(url_for('home'))


# Admin access is granted only by the project owner from the Flask CLI.
@app.cli.command('list-admins')
def list_admins():
    """List accounts that currently have admin access."""
    cur = conn.cursor()
    cur.execute("SELECT name, email FROM users WHERE role='admin' ORDER BY user_id")
    admins = cur.fetchall()

    if not admins:
        click.echo('No admin accounts are configured.')
        return

    for name, email in admins:
        click.echo(f'{name} <{email}>')
    click.echo(f'Total: {len(admins)} admin account(s)')


@app.cli.command('init-translations')
def init_translations():
    """Add account language preferences and reviewed content translations."""
    cur = conn.cursor()
    try:
        cur.execute((BASE_DIR / 'translations_schema.sql').read_text(encoding='utf-8'))
        conn.commit()
    except Exception as error:
        conn.rollback()
        raise click.ClickException(f'Translation setup failed: {error}') from error
    click.echo('Language preference and content translation storage are ready.')


@app.cli.command('seed-fertilizer-translations')
def seed_fertilizer_translation_content():
    """Publish reviewed Hindi and Marathi fertilizer catalog translations."""
    cur = conn.cursor()
    try:
        fertilizer_count, prepared_count, inserted_count = seed_fertilizer_translations(cur)
        conn.commit()
    except (KeyError, AttributeError, psycopg2.Error) as error:
        conn.rollback()
        raise click.ClickException(f'Fertilizer translation setup failed: {error}') from error
    click.echo(
        f'Prepared {prepared_count} translations for {fertilizer_count} fertilizers; '
        f'inserted {inserted_count} new translations.'
    )


@app.cli.command('seed-crop-translations')
def seed_crop_translation_content():
    """Publish reviewed Hindi and Marathi crop catalog translations."""
    cur = conn.cursor()
    try:
        crop_count, prepared_count, inserted_count = seed_crop_translations(cur)
        conn.commit()
    except (KeyError, AttributeError, psycopg2.Error) as error:
        conn.rollback()
        raise click.ClickException(f'Crop translation setup failed: {error}') from error
    click.echo(
        f'Prepared {prepared_count} translations for {crop_count} crops; '
        f'inserted {inserted_count} new translations.'
    )


@app.cli.command('seed-loan-translations')
def seed_loan_translation_content():
    """Publish reviewed Hindi and Marathi loan/scheme translations."""
    cur = conn.cursor()
    try:
        loan_count, prepared_count, inserted_count = seed_loan_translations(cur)
        conn.commit()
    except (KeyError, AttributeError, psycopg2.Error) as error:
        conn.rollback()
        raise click.ClickException(f'Loan translation setup failed: {error}') from error
    click.echo(
        f'Prepared {prepared_count} translations for {loan_count} loan records; '
        f'inserted {inserted_count} new translations.'
    )


@app.cli.command('grant-admin')
@click.argument('email')
def grant_admin(email):
    """Grant admin access while enforcing the two-admin limit."""
    cur = conn.cursor()
    cur.execute("SELECT user_id, role FROM users WHERE LOWER(email)=LOWER(%s)", (email.strip(),))
    account = cur.fetchone()

    if not account:
        raise click.ClickException('No registered account uses that email address.')
    if account[1] == 'admin':
        click.echo('This account already has admin access.')
        return

    cur.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cur.fetchone()[0] >= MAX_ADMIN_ACCOUNTS:
        raise click.ClickException(
            f'The limit of {MAX_ADMIN_ACCOUNTS} admins has been reached. Revoke one first.'
        )

    cur.execute("UPDATE users SET role='admin' WHERE user_id=%s", (account[0],))
    conn.commit()
    click.echo('Admin access granted.')


@app.cli.command('revoke-admin')
@click.argument('email')
def revoke_admin(email):
    """Change an admin account back to a normal user account."""
    cur = conn.cursor()
    cur.execute("SELECT user_id, role FROM users WHERE LOWER(email)=LOWER(%s)", (email.strip(),))
    account = cur.fetchone()

    if not account or account[1] != 'admin':
        raise click.ClickException('That email does not belong to an admin account.')

    cur.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cur.fetchone()[0] <= 1:
        raise click.ClickException('The final admin account cannot be revoked.')

    cur.execute("UPDATE users SET role='user' WHERE user_id=%s", (account[0],))
    conn.commit()
    click.echo('Admin access revoked; the account is now a normal user.')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/api/language', methods=['POST'])
def update_language():
    if session.get('role') not in {'user', 'admin'}:
        return jsonify({'error': 'Please log in to save a language preference.'}), 401

    language = str((request.get_json(silent=True) or {}).get('language', '')).strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported language.'}), 400

    user_id = current_user_id()
    if not user_id:
        return jsonify({'error': 'Please log in again.'}), 401

    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET preferred_language=%s WHERE user_id=%s",
            (language, user_id),
        )
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Language preference could not be saved')
        return jsonify({'error': 'Language preference could not be saved.'}), 503

    session['language'] = language
    return jsonify({'language': language})


# ================= DISEASE DETECTION =================
DISEASE_TEXT = {
    'hi': {
        'healthy': 'स्वस्थ पत्ती',
        'crop.Potato': 'आलू', 'crop.Raspberry': 'रास्पबेरी',
        'crop.Soybean': 'सोयाबीन', 'crop.Squash': 'स्क्वैश',
        'crop.Strawberry': 'स्ट्रॉबेरी', 'crop.Tomato': 'टमाटर',
        'condition.Early blight': 'अगेती झुलसा', 'condition.Late blight': 'पछेती झुलसा',
        'condition.Powdery mildew': 'चूर्णिल आसिता', 'condition.Leaf scorch': 'पत्ती झुलसन',
        'condition.Bacterial spot': 'जीवाणु धब्बा', 'condition.Leaf Mold': 'पत्ती फफूंद',
        'condition.Septoria leaf spot': 'सेप्टोरिया पत्ती धब्बा',
        'condition.Spider mites Two-spotted spider mite': 'दो-धब्बेदार मकड़ी घुन',
        'condition.Target Spot': 'टार्गेट स्पॉट',
        'condition.Tomato Yellow Leaf Curl Virus': 'टमाटर पीला पत्ती मोड़ विषाणु',
        'condition.Tomato mosaic virus': 'टमाटर मोज़ेक विषाणु',
        'rec.healthy1': 'इस चित्र में कोई समर्थित रोग नहीं मिला।',
        'rec.healthy2': 'नियमित निरीक्षण, सिंचाई और संतुलित पोषण जारी रखें।',
        'rec.healthy3': 'यदि पौधे में असामान्य लक्षण हों तो एक और साफ चित्र जाँचें।',
        'rec.separate': 'प्रभावित पौधों को अलग करें या बहुत खराब पत्तियाँ हटा दें।',
        'rec.tools': 'प्रभावित पौधों को छूने के बाद औजारों को कीटाणुरहित करें।',
        'rec.expert': 'उपचार से पहले स्थानीय कृषि विशेषज्ञ से परिणाम की पुष्टि करें।',
        'rec.virus': 'विषाणु फैलाने वाली सफेद मक्खी और माहू जैसे रस चूसने वाले कीटों का नियंत्रण करें।',
        'rec.mites': 'पत्तियों की निचली सतह और पास के पौधों पर घुन तथा महीन जाले देखें।',
        'rec.fungal': 'हवा का आवागमन सुधारें और सिंचाई के समय पत्तियों को गीला करने से बचें।',
    },
    'mr': {
        'healthy': 'निरोगी पान',
        'crop.Potato': 'बटाटा', 'crop.Raspberry': 'रास्पबेरी',
        'crop.Soybean': 'सोयाबीन', 'crop.Squash': 'स्क्वॅश',
        'crop.Strawberry': 'स्ट्रॉबेरी', 'crop.Tomato': 'टोमॅटो',
        'condition.Early blight': 'लवकर करपा', 'condition.Late blight': 'उशिरा करपा',
        'condition.Powdery mildew': 'भुरी', 'condition.Leaf scorch': 'पान करपणे',
        'condition.Bacterial spot': 'जिवाणूजन्य ठिपके', 'condition.Leaf Mold': 'पानावरील बुरशी',
        'condition.Septoria leaf spot': 'सेप्टोरिया पानावरील ठिपके',
        'condition.Spider mites Two-spotted spider mite': 'दोन ठिपक्यांचा कोळी माइट',
        'condition.Target Spot': 'टार्गेट स्पॉट',
        'condition.Tomato Yellow Leaf Curl Virus': 'टोमॅटो पिवळा पर्णगुंडाळी विषाणू',
        'condition.Tomato mosaic virus': 'टोमॅटो मोझॅक विषाणू',
        'rec.healthy1': 'या चित्रात कोणताही समर्थित रोग आढळला नाही.',
        'rec.healthy2': 'नियमित निरीक्षण, सिंचन आणि संतुलित पोषण सुरू ठेवा.',
        'rec.healthy3': 'झाडावर असामान्य लक्षणे असल्यास दुसरे स्पष्ट चित्र तपासा.',
        'rec.separate': 'बाधित झाडे वेगळी करा किंवा खूप खराब झालेली पाने काढा.',
        'rec.tools': 'बाधित झाडे हाताळल्यानंतर साधने निर्जंतुक करा.',
        'rec.expert': 'उपचार करण्यापूर्वी स्थानिक कृषी तज्ज्ञांकडून निकालाची खात्री करा.',
        'rec.virus': 'विषाणू पसरवणाऱ्या पांढरी माशी आणि मावा यांसारख्या रसशोषक किडींचे नियंत्रण करा.',
        'rec.mites': 'पानांच्या खालच्या बाजूस आणि जवळच्या झाडांवर माइट्स व बारीक जाळी तपासा.',
        'rec.fungal': 'हवेचा प्रवाह सुधारा आणि सिंचनाच्या वेळी पाने ओली करणे टाळा.',
    },
}


def disease_text(key, language, fallback):
    return DISEASE_TEXT.get(language, {}).get(key, fallback)


def disease_recommendations(raw_label, language='en'):
    label = raw_label.lower()

    if 'healthy' in label:
        return [
            disease_text('rec.healthy1', language, 'No supported disease was detected in this image.'),
            disease_text('rec.healthy2', language, 'Continue routine monitoring, irrigation, and balanced nutrition.'),
            disease_text('rec.healthy3', language, 'Check another clear image if the plant still shows unusual symptoms.')
        ]

    recommendations = [
        disease_text('rec.separate', language, 'Separate affected plants or remove badly damaged leaves.'),
        disease_text('rec.tools', language, 'Disinfect tools after handling affected plants.'),
        disease_text('rec.expert', language, 'Confirm the result with a local agricultural expert before applying treatment.')
    ]

    if 'virus' in label:
        recommendations.insert(1, disease_text('rec.virus', language, 'Control sap-feeding insects such as whiteflies and aphids, which can spread viruses.'))
    elif 'spider_mite' in label or 'spider mites' in label:
        recommendations.insert(1, disease_text('rec.mites', language, 'Inspect leaf undersides and nearby plants for mites and fine webbing.'))
    elif any(term in label for term in ('blight', 'spot', 'mold', 'mildew', 'scorch')):
        recommendations.insert(1, disease_text('rec.fungal', language, 'Improve air circulation and avoid wetting foliage during irrigation.'))

    return recommendations


def format_disease_result(raw_label, confidence, language='en'):
    crop_name, _, condition = raw_label.partition('___')
    crop_name = crop_name.replace('_', ' ').strip()
    condition = (condition or raw_label).replace('_', ' ').strip()
    is_healthy = condition.lower() == 'healthy'

    return {
        'crop': disease_text(f'crop.{crop_name}', language, crop_name),
        'disease': disease_text('healthy', language, 'Healthy leaf') if is_healthy else disease_text(f'condition.{condition}', language, condition),
        'confidence': round(float(confidence), 2),
        'healthy': is_healthy,
        'recommendations': disease_recommendations(raw_label, language)
    }


@app.route('/disease')
def disease_page():
    if session.get('role') not in {'user', 'admin'}:
        return redirect(url_for('home'))
    return render_template('templates/disesase/disease.html')


@app.route('/detect-disease', methods=['POST'])
def detect_disease():
    if session.get('role') not in {'user', 'admin'}:
        return jsonify({'error': 'Please log in before using disease detection.'}), 401

    uploaded_image = request.files.get('image')

    if not uploaded_image or not uploaded_image.filename:
        return jsonify({'error': 'Please select a leaf image.'}), 400

    extension = Path(uploaded_image.filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({'error': 'Only JPG, PNG, and WEBP images are supported.'}), 400

    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        return jsonify({'error': 'Image support is not installed on the server. Install the project requirements.'}), 503

    try:
        with Image.open(uploaded_image.stream) as image:
            image.verify()
        uploaded_image.stream.seek(0)
    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify({'error': 'The uploaded file is not a valid image.'}), 400

    try:
        from predict import predict_disease
        raw_label, confidence = predict_disease(uploaded_image.stream)
        result = format_disease_result(raw_label, confidence, selected_language())
    except Exception:
        app.logger.exception('Disease prediction failed')
        return jsonify({'error': 'The AI model could not analyse this image.'}), 500

    # Analytics recording is additive: prediction results still reach the farmer
    # even if analytics storage has a temporary problem.
    user_id = current_user_id() if session.get('role') == 'user' else None
    if user_id:
        analytics_cursor = conn.cursor()
        try:
            record_disease_detection(
                analytics_cursor,
                user_id,
                result['crop'],
                result['disease'],
                result['confidence'],
                secure_filename(uploaded_image.filename)[:255] or None,
            )
            conn.commit()
        except psycopg2.Error:
            conn.rollback()
            app.logger.exception('Disease analytics could not be recorded')

    if request.accept_mimetypes.best == 'application/json':
        return jsonify(result)

    return render_template(
        'templates/disesase/disease_result.html',
        disease=result['disease'],
        confidence=result['confidence']
    )


@app.errorhandler(413)
def image_too_large(_error):
    return jsonify({'error': 'The selected image is larger than 10 MB.'}), 413

# ================= ADMIN DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if session.get('role') == 'admin':
        return render_template('templates/admin/dashboard.html')

    return redirect('/')

# ================= USER DASHBOARD =================
@app.route('/user-dashboard')
def user_dashboard():
    if session.get('role') == 'user':
        return render_template("app.html")

    return redirect('/')


@app.route('/api/dashboard-data')
def dashboard_data():
    """Return the latest admin-managed content for the user SPA."""
    if session.get('role') not in {'user', 'admin'}:
        return jsonify({'error': 'Please log in to view dashboard data.'}), 401

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT crop_id, name, scientific_name, category, season, duration,
                   soil, ph_range, temperature, rainfall, yield_per_acre,
                   market_price, estimated_profit
            FROM crops ORDER BY name
        """)
        crops = [
            {
                'id': row[0], 'name': row[1], 'scientificName': row[2],
                'category': row[3], 'season': row[4], 'duration': row[5],
                'soil': row[6], 'pH': row[7], 'temperature': row[8],
                'rainfall': row[9], 'yieldPerAcre': row[10],
                'marketPrice': row[11], 'estimatedProfit': row[12]
            }
            for row in cur.fetchall()
        ]

        cur.execute("""
            SELECT fertilizer_id, name, type, nutrients, dosage, description
            FROM fertilizers ORDER BY name
        """)
        fertilizers = [
            {
                'id': row[0], 'name': row[1], 'type': row[2],
                'nutrients': row[3], 'dosage': row[4], 'description': row[5]
            }
            for row in cur.fetchall()
        ]

        cur.execute("""
            SELECT loan_id, name, short_name, type, region, description,
                   interest, max_amount, benefits
            FROM loans ORDER BY name
        """)
        loans = [
            {
                'id': row[0], 'name': row[1], 'shortName': row[2],
                'type': row[3], 'region': row[4], 'description': row[5],
                'interest': row[6], 'maxAmount': row[7], 'benefits': row[8]
            }
            for row in cur.fetchall()
        ]

        language = selected_language()
        apply_record_translations(cur, 'crop', crops, language, {
            'name': 'name', 'category': 'category', 'season': 'season',
            'duration': 'duration', 'soil': 'soil', 'ph_range': 'pH',
            'temperature': 'temperature', 'rainfall': 'rainfall',
            'yield_per_acre': 'yieldPerAcre', 'market_price': 'marketPrice',
            'estimated_profit': 'estimatedProfit',
        })
        apply_record_translations(cur, 'fertilizer', fertilizers, language, {
            'name': 'name', 'type': 'type', 'nutrients': 'nutrients',
            'dosage': 'dosage', 'description': 'description',
        })
        apply_record_translations(cur, 'loan', loans, language, {
            'name': 'name', 'short_name': 'shortName', 'type': 'type',
            'region': 'region', 'description': 'description',
            'interest': 'interest', 'max_amount': 'maxAmount',
            'benefits': 'benefits',
        })
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Dashboard data could not be loaded')
        return jsonify({'error': 'Agricultural information is temporarily unavailable.'}), 503

    response = jsonify({
        'crops': crops,
        'fertilizers': fertilizers,
        'loans': loans
    })
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/api/dashboard-stats')
def dashboard_stats():
    """Return lightweight, live totals for dashboard summary cards."""
    if session.get('role') not in {'user', 'admin'}:
        return jsonify({'error': 'Please log in to view dashboard statistics.'}), 401

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM crops),
                (SELECT COUNT(*) FROM fertilizers),
                (SELECT COUNT(*) FROM loans),
                (SELECT COUNT(*) FROM users WHERE role='user'),
                (SELECT COUNT(*) FROM disease_detection_history),
                (SELECT COUNT(*) FROM farmer_activity)
        """)
        row = cur.fetchone()
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Dashboard statistics could not be loaded')
        return jsonify({'error': 'Dashboard totals are temporarily unavailable.'}), 503

    response = jsonify({
        'crops': row[0],
        'fertilizers': row[1],
        'loans': row[2],
        'farmers': row[3],
        'diseaseDetections': row[4],
        'activities': row[5],
    })
    response.headers['Cache-Control'] = 'no-store'
    return response


# ================= FARMER ANALYTICS =================
@app.cli.command('init-analytics')
def init_analytics():
    """Create the additive farmer analytics tables and indexes."""
    cur = conn.cursor()
    try:
        cur.execute((BASE_DIR / 'analytics_schema.sql').read_text(encoding='utf-8'))
        conn.commit()
    except Exception as error:
        conn.rollback()
        raise click.ClickException(f'Analytics setup failed: {error}') from error
    click.echo('Farmer analytics tables are ready.')


def optional_positive_integer(value):
    if value in (None, ''):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError('Resource IDs must be numbers.')
    if parsed <= 0:
        raise ValueError('Resource IDs must be positive.')
    return parsed


@app.route('/api/farmer-activity', methods=['POST'])
def farmer_activity():
    if session.get('role') != 'user':
        return jsonify({'error': 'A farmer login is required.'}), 401

    user_id = current_user_id()
    if not user_id:
        return jsonify({'error': 'Please log in again to enable activity tracking.'}), 401

    payload = request.get_json(silent=True) or {}
    activity_type = str(payload.get('activity_type', '')).strip()
    if activity_type not in ALLOWED_ACTIVITY_TYPES:
        return jsonify({'error': 'Unsupported activity type.'}), 400

    try:
        crop_id = optional_positive_integer(payload.get('crop_id'))
        fertilizer_id = optional_positive_integer(payload.get('fertilizer_id'))
        loan_id = optional_positive_integer(payload.get('loan_id'))
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    raw_details = payload.get('details') if isinstance(payload.get('details'), dict) else {}
    details = {
        str(key)[:40]: str(value)[:160]
        for key, value in list(raw_details.items())[:5]
    }

    cur = conn.cursor()
    try:
        activity_id = record_activity(
            cur,
            user_id,
            activity_type,
            crop_id=crop_id,
            fertilizer_id=fertilizer_id,
            loan_id=loan_id,
            details=details,
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'The selected crop, fertilizer, or loan does not exist.'}), 400
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Farmer activity could not be recorded')
        return jsonify({'error': 'Activity could not be recorded.'}), 500

    return jsonify({'recorded': True, 'activityId': activity_id}), 201


@app.route('/admin/api/analytics')
def admin_analytics():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Administrator access is required.'}), 403

    period = request.args.get('period', 'all')
    if period not in {'all', '7d', '30d', 'year'}:
        return jsonify({'error': 'Unsupported date range.'}), 400

    try:
        crop_id = optional_positive_integer(request.args.get('crop_id'))
        fertilizer_id = optional_positive_integer(request.args.get('fertilizer_id'))
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    disease = request.args.get('disease', '').strip()[:180] or None
    activity_type = request.args.get('activity_type', '').strip() or None
    if activity_type and activity_type not in ALLOWED_ACTIVITY_TYPES:
        return jsonify({'error': 'Unsupported activity type.'}), 400

    filters = {
        'period': period,
        'crop_id': crop_id,
        'fertilizer_id': fertilizer_id,
        'disease': disease,
        'activity_type': activity_type,
    }

    cur = conn.cursor()
    try:
        analytics = get_admin_analytics(cur, filters)
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Admin analytics could not be loaded')
        return jsonify({
            'error': 'Analytics data is not initialized. Run: flask --app app init-analytics'
        }), 503

    response = jsonify(analytics)
    response.headers['Cache-Control'] = 'no-store'
    return response


# ================= SMART AGRICULTURAL CALENDAR =================
def calendar_api_access_allowed():
    return session.get('role') in {'user', 'admin'}


@app.cli.command('init-calendar')
def init_calendar():
    """Create and seed the additive Smart Agricultural Calendar tables."""
    cur = conn.cursor()
    try:
        cur.execute((BASE_DIR / 'smart_calendar_schema.sql').read_text(encoding='utf-8'))
        cur.execute((BASE_DIR / 'smart_calendar_seed.sql').read_text(encoding='utf-8'))
        cur.execute((BASE_DIR / 'smart_calendar_expansion_seed.sql').read_text(encoding='utf-8'))
        conn.commit()
    except Exception as error:
        conn.rollback()
        raise click.ClickException(f'Calendar setup failed: {error}') from error
    click.echo('Smart Agricultural Calendar tables and verified starter profiles are ready.')


@app.route('/api/calendar/options')
def calendar_options():
    """Return only crops that have an active, verified preplanned profile."""
    if not calendar_api_access_allowed():
        return jsonify({'error': 'Please log in to view the agricultural calendar.'}), 401

    try:
        selected_year = int(request.args.get('year', date.today().year))
    except (TypeError, ValueError):
        return jsonify({'error': 'The calendar year must be a number.'}), 400

    if selected_year < 2000 or selected_year > 2100:
        return jsonify({'error': 'The calendar year is outside the supported range.'}), 400

    cur = conn.cursor()
    try:
        language = selected_language()
        crops = list_calendar_crops(cur, selected_year, language)
        plant_now = crops_to_plant_this_month(cur, date.today().month, language)
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Calendar options could not be loaded')
        return jsonify({
            'error': 'Calendar data is not initialized. Run: flask --app app init-calendar'
        }), 503

    response = jsonify({
        'year': selected_year,
        'currentMonth': date.today().month,
        'crops': crops,
        'plantThisMonth': plant_now,
        'selectionRequired': 'crop_only'
    })
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/api/calendar/<int:crop_id>')
def crop_calendar(crop_id):
    """Generate a complete plan from stored rules; no farmer-entered dates."""
    if not calendar_api_access_allowed():
        return jsonify({'error': 'Please log in to view the agricultural calendar.'}), 401

    try:
        selected_year = int(request.args.get('year', date.today().year))
    except (TypeError, ValueError):
        return jsonify({'error': 'The calendar year must be a number.'}), 400

    if selected_year < 2000 or selected_year > 2100:
        return jsonify({'error': 'The calendar year is outside the supported range.'}), 400

    cur = conn.cursor()
    try:
        calendar = build_crop_calendar(cur, crop_id, selected_year, selected_language())
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Crop calendar could not be generated')
        return jsonify({'error': 'The preplanned calendar could not be loaded.'}), 500

    if calendar is None:
        return jsonify({'error': 'This crop does not have a verified calendar profile yet.'}), 404

    response = jsonify(calendar)
    response.headers['Cache-Control'] = 'no-store'
    return response


# ==================================================
# ================= CROPS ===========================
# ==================================================

@app.route('/admin/translations')
def manage_translations():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    cur = conn.cursor()
    try:
        resources = {}
        for entity_type, table, id_column in (
            ('crop', 'crops', 'crop_id'),
            ('fertilizer', 'fertilizers', 'fertilizer_id'),
            ('loan', 'loans', 'loan_id'),
        ):
            cur.execute(f'SELECT {id_column}, name FROM {table} ORDER BY name')
            resources[entity_type] = [
                {'id': row[0], 'name': row[1]} for row in cur.fetchall()
            ]

        cur.execute("""
            SELECT a.activity_id, c.name || ' — ' || a.title
            FROM farming_activities a
            JOIN crop_calendar_profiles p ON p.profile_id=a.profile_id
            JOIN crops c ON c.crop_id=p.crop_id
            ORDER BY c.name, a.start_day, a.activity_id
        """)
        resources['calendar_activity'] = [
            {'id': row[0], 'name': row[1]} for row in cur.fetchall()
        ]
        cur.execute("""
            SELECT p.profile_id, c.name || ' calendar profile'
            FROM crop_calendar_profiles p
            JOIN crops c ON c.crop_id=p.crop_id
            ORDER BY c.name, p.profile_id
        """)
        resources['calendar_profile'] = [
            {'id': row[0], 'name': row[1]} for row in cur.fetchall()
        ]
        cur.execute("""
            SELECT r.risk_id, c.name || ' — ' || r.disease_name
            FROM crop_disease_risks r
            JOIN crop_calendar_profiles p ON p.profile_id=r.profile_id
            JOIN crops c ON c.crop_id=p.crop_id
            ORDER BY c.name, r.start_day, r.risk_id
        """)
        resources['calendar_risk'] = [
            {'id': row[0], 'name': row[1]} for row in cur.fetchall()
        ]

        cur.execute("""
            SELECT translation_id, entity_type, entity_id, field_name,
                   language_code, translated_text, updated_at
            FROM content_translations
            ORDER BY updated_at DESC, translation_id DESC
        """)
        translations = cur.fetchall()
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Translation management data could not be loaded')
        flash('Translations could not be loaded. Run: flask --app app init-translations', 'error')
        resources = {'crop': [], 'fertilizer': [], 'loan': []}
        translations = []

    resource_names = {
        (entity_type, item['id']): item['name']
        for entity_type, items in resources.items()
        for item in items
    }
    return render_template(
        'templates/admin/translations.html',
        resources=resources,
        fields={key: sorted(value) for key, value in TRANSLATABLE_FIELDS.items()},
        translations=translations,
        resource_names=resource_names,
    )


@app.route('/admin/translations/save', methods=['POST'])
def save_translation():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    entity_type = request.form.get('entity_type', '').strip()
    field_name = request.form.get('field_name', '').strip()
    language = request.form.get('language_code', '').strip().lower()
    translated_text = request.form.get('translated_text', '').strip()
    try:
        entity_id = int(request.form.get('entity_id', ''))
    except (TypeError, ValueError):
        entity_id = 0

    if (
        entity_type not in TRANSLATABLE_FIELDS
        or field_name not in TRANSLATABLE_FIELDS[entity_type]
        or language not in {'hi', 'mr'}
        or entity_id <= 0
        or not translated_text
    ):
        flash('Please select a valid record, field, language, and translation.', 'error')
        return redirect(url_for('manage_translations'))

    entity_tables = {
        'crop': ('crops', 'crop_id'),
        'fertilizer': ('fertilizers', 'fertilizer_id'),
        'loan': ('loans', 'loan_id'),
        'calendar_profile': ('crop_calendar_profiles', 'profile_id'),
        'calendar_activity': ('farming_activities', 'activity_id'),
        'calendar_risk': ('crop_disease_risks', 'risk_id'),
    }
    table, id_column = entity_tables[entity_type]
    cur = conn.cursor()
    try:
        cur.execute(f'SELECT 1 FROM {table} WHERE {id_column}=%s', (entity_id,))
        if not cur.fetchone():
            conn.rollback()
            flash('The selected database record no longer exists.', 'error')
            return redirect(url_for('manage_translations'))

        cur.execute("""
            INSERT INTO content_translations
                (entity_type, entity_id, field_name, language_code,
                 translated_text, reviewed, updated_at)
            VALUES (%s,%s,%s,%s,%s,TRUE,CURRENT_TIMESTAMP)
            ON CONFLICT (entity_type, entity_id, field_name, language_code)
            DO UPDATE SET translated_text=EXCLUDED.translated_text,
                          reviewed=TRUE,
                          updated_at=CURRENT_TIMESTAMP
        """, (entity_type, entity_id, field_name, language, translated_text))
        conn.commit()
        flash('Translation saved and published.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Translation could not be saved')
        flash('The translation could not be saved.', 'error')

    return redirect(url_for('manage_translations'))


@app.route('/admin/translations/<int:translation_id>/delete', methods=['POST'])
def delete_translation(translation_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    cur = conn.cursor()
    try:
        cur.execute(
            'DELETE FROM content_translations WHERE translation_id=%s',
            (translation_id,),
        )
        conn.commit()
        flash('Translation deleted.' if cur.rowcount else 'Translation was not found.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Translation could not be deleted')
        flash('The translation could not be deleted.', 'error')
    return redirect(url_for('manage_translations'))

def required_form_values(field_names):
    values = tuple(request.form.get(field, '').strip() for field in field_names)
    return values if all(values) else None

@app.route('/admin/crops')
def manage_crops():
    if session.get('role') == 'admin':

        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM crops ORDER BY name")
            data = cur.fetchall()
        except psycopg2.Error:
            conn.rollback()
            app.logger.exception('Admin crop list could not be loaded')
            flash('Crops could not be loaded right now.', 'error')
            data = []

        return render_template('templates/admin/crop.html', crops=data)

    return redirect('/')


@app.route('/add-crop', methods=['POST'])
def add_crop():

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    data = required_form_values((
        'name', 'scientific_name', 'category', 'season', 'duration', 'soil',
        'ph_range', 'temperature', 'rainfall', 'yield_per_acre',
        'market_price', 'estimated_profit'
    ))
    if not data:
        flash('Please complete every crop field.', 'error')
        return redirect(url_for('manage_crops'))

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO crops
            (name, scientific_name, category, season, duration, soil, ph_range,
            temperature, rainfall, yield_per_acre, market_price, estimated_profit)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)
        conn.commit()
        flash('Crop added successfully.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Crop could not be added')
        flash('The crop could not be added. Please try again.', 'error')

    return redirect(url_for('manage_crops'))


@app.route('/delete-crop/<int:id>', methods=['POST'])
def delete_crop(id):

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM crops WHERE crop_id=%s", (id,))
        conn.commit()
        flash('Crop deleted.' if cur.rowcount else 'Crop was not found.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Crop could not be deleted')
        flash('The crop could not be deleted because it is still in use.', 'error')

    return redirect(url_for('manage_crops'))


# ==================================================
# ================= FERTILIZER ======================
# ==================================================

@app.route('/admin/fertilizer')
def manage_fertilizer():

    if session.get('role') == 'admin':

        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM fertilizers ORDER BY name")
            data = cur.fetchall()
        except psycopg2.Error:
            conn.rollback()
            app.logger.exception('Admin fertilizer list could not be loaded')
            flash('Fertilizers could not be loaded right now.', 'error')
            data = []

        return render_template(
            'templates/admin/fertilizer.html',
            fertilizers=data
        )

    return redirect('/')


@app.route('/add-fertilizer', methods=['POST'])
def add_fertilizer():

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    data = required_form_values(('name', 'type', 'nutrients', 'dosage', 'description'))
    if not data:
        flash('Please complete every fertilizer field.', 'error')
        return redirect(url_for('manage_fertilizer'))

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO fertilizers
            (name, type, nutrients, dosage, description)
            VALUES (%s,%s,%s,%s,%s)
        """, data)
        conn.commit()
        flash('Fertilizer added successfully.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Fertilizer could not be added')
        flash('The fertilizer could not be added. Please try again.', 'error')

    return redirect(url_for('manage_fertilizer'))


@app.route('/delete-fertilizer/<int:id>', methods=['POST'])
def delete_fertilizer(id):

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM fertilizers WHERE fertilizer_id=%s", (id,))
        conn.commit()
        flash('Fertilizer deleted.' if cur.rowcount else 'Fertilizer was not found.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Fertilizer could not be deleted')
        flash('The fertilizer could not be deleted because it is still in use.', 'error')

    return redirect(url_for('manage_fertilizer'))


# ==================================================
# ================= LOANS ===========================
# ==================================================

@app.route('/admin/loans')
def manage_loans():

    if session.get('role') == 'admin':

        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM loans ORDER BY name")
            data = cur.fetchall()
        except psycopg2.Error:
            conn.rollback()
            app.logger.exception('Admin loan list could not be loaded')
            flash('Loans could not be loaded right now.', 'error')
            data = []

        return render_template(
            'templates/admin/loans.html',
            loans=data
        )

    return redirect('/')


@app.route('/add-loan', methods=['POST'])
def add_loan():

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    data = required_form_values((
        'name', 'short_name', 'type', 'region', 'description', 'interest',
        'max_amount', 'benefits'
    ))
    if not data:
        flash('Please complete every loan field.', 'error')
        return redirect(url_for('manage_loans'))

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO loans
            (name, short_name, type, region, description, interest,
            max_amount, benefits)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)
        conn.commit()
        flash('Loan or scheme added successfully.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Loan could not be added')
        flash('The loan or scheme could not be added. Please try again.', 'error')

    return redirect(url_for('manage_loans'))


@app.route('/delete-loan/<int:id>', methods=['POST'])
def delete_loan(id):

    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM loans WHERE loan_id=%s", (id,))
        conn.commit()
        flash('Loan or scheme deleted.' if cur.rowcount else 'Loan or scheme was not found.', 'success')
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Loan could not be deleted')
        flash('The loan or scheme could not be deleted because it is still in use.', 'error')

    return redirect(url_for('manage_loans'))


@app.route('/get-crops')
def get_crops():
    if session.get('role') not in {'user', 'admin'}:
        return jsonify({'error': 'Please log in to view crop data.'}), 401

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT crop_id, name, scientific_name, category, season, duration,
                   soil, ph_range, temperature, rainfall, yield_per_acre,
                   market_price, estimated_profit
            FROM crops ORDER BY name
        """)
        crops = cur.fetchall()
    except psycopg2.Error:
        conn.rollback()
        app.logger.exception('Crop API could not be loaded')
        return jsonify({'error': 'Crop information is temporarily unavailable.'}), 503

    crop_list = []

    for crop in crops:
        crop_list.append({
            "crop_id": crop[0],
            "name": crop[1],
            "scientific_name": crop[2],
            "category": crop[3],
            "season": crop[4],
            "duration": crop[5],
            "soil": crop[6],
            "ph_range": crop[7],
            "temperature": crop[8],
            "rainfall": crop[9],
            "yield_per_acre": crop[10],
            "market_price": crop[11],
            "estimated_profit": crop[12]
        })

    return jsonify(crop_list)


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
