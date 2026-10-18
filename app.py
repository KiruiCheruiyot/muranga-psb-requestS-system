import os
import secrets
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "requests.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
# Convenient fallback for local classroom/demo use. Set SECRET_KEY in deployment.
if not SECRET_KEY:
    SECRET_KEY = "local-demo-only-change-this-secret-key"
app.secret_key = SECRET_KEY
app.config.update(
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
)


def generate_csrf_token():
    """Return a per-session synchronizer token for HTML forms."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = generate_csrf_token


@app.before_request
def protect_post_requests():
    """Reject state-changing form submissions without a valid CSRF token."""
    if request.method == "POST":
        supplied = request.form.get("csrf_token", "")
        expected = session.get("_csrf_token", "")
        if not supplied or not expected or not secrets.compare_digest(supplied, expected):
            abort(400, description="The form security token is missing or expired. Please reload the page and try again.")

CATEGORIES = [
    "Broken Streetlight",
    "Water Supply Issue",
    "Garbage Collection",
    "Roads and Drainage",
    "Public Health and Sanitation",
    "Other Public Service Issue",
]
STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'citizen',
                created_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT 'Not provided',
                image_filename TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_note TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
            # Add new fields safely when upgrading an existing demo database.
        columns = {row[1] for row in db.execute("PRAGMA table_info(service_requests)").fetchall()}
        if "location" not in columns:
            db.execute("ALTER TABLE service_requests ADD COLUMN location TEXT NOT NULL DEFAULT 'Not provided'")
        if "image_filename" not in columns:
            db.execute("ALTER TABLE service_requests ADD COLUMN image_filename TEXT DEFAULT ''")
        db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                request_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (request_id) REFERENCES service_requests(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS request_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                old_status TEXT NOT NULL DEFAULT '',
                new_status TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                changed_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (request_id) REFERENCES service_requests(id)
            )
        """)
        # Optional first administrator. Set ADMIN_EMAIL and ADMIN_PASSWORD in deployment settings.
        admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if admin_email and admin_password:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
            if not existing:
                db.execute(
                    "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
                    ("PSB Administrator", admin_email, generate_password_hash(admin_password), datetime.utcnow().isoformat(timespec="seconds"))
                )


init_db()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def make_reference():
    return "MPSB-" + datetime.utcnow().strftime("%y%m%d") + "-" + secrets.token_hex(3).upper()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "citizen").strip().lower()
        # This is an openly configurable classroom demo, so users can choose a role at sign-up.
        # Do not enable this pattern on a real public service website.
        if role not in {"citizen", "admin"}:
            role = "citizen"
        if not full_name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password with at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (full_name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                    (full_name, email, generate_password_hash(password), role, datetime.utcnow().isoformat(timespec="seconds"))
                )
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["full_name"]
            session["role"] = user["role"]
            flash("Welcome back.", "success")
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM service_requests WHERE user_id = ? ORDER BY id DESC",
            (session["user_id"],)
        ).fetchall()
        request_stats = {
            "total": db.execute("SELECT COUNT(*) FROM service_requests WHERE user_id = ?", (session["user_id"],)).fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM service_requests WHERE user_id = ? AND status = 'Pending'", (session["user_id"],)).fetchone()[0],
            "progress": db.execute("SELECT COUNT(*) FROM service_requests WHERE user_id = ? AND status = 'In Progress'", (session["user_id"],)).fetchone()[0],
            "resolved": db.execute("SELECT COUNT(*) FROM service_requests WHERE user_id = ? AND status = 'Resolved'", (session["user_id"],)).fetchone()[0],
        }
        notifications = db.execute(
            "SELECT n.*, r.reference FROM notifications n JOIN service_requests r ON r.id = n.request_id "
            "WHERE n.user_id = ? ORDER BY n.id DESC LIMIT 10", (session["user_id"],)
        ).fetchall()
    return render_template("dashboard.html", requests=rows, notifications=notifications, stats=request_stats)


@app.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    if request.method == "POST":
        category = request.form.get("category", "")
        subject = request.form.get("subject", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        uploaded = request.files.get("image")
        image_filename = ""
        if uploaded and uploaded.filename:
            original = secure_filename(uploaded.filename)
            ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
            if ext not in ALLOWED_EXTENSIONS:
                flash("Upload an image in PNG, JPG, JPEG, GIF, or WEBP format.", "error")
                return render_template("new_request.html", categories=CATEGORIES)
            image_filename = secrets.token_hex(12) + "." + ext
        if category not in CATEGORIES or not subject or not description or not location:
            flash("Please complete all required fields and choose a valid category.", "error")
            return render_template("new_request.html", categories=CATEGORIES)
        if uploaded and uploaded.filename and image_filename:
            uploaded.save(os.path.join(UPLOAD_FOLDER, image_filename))
        reference = make_reference()
        now = datetime.utcnow().isoformat(timespec="seconds")
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO service_requests
                (reference, user_id, category, subject, description, location, image_filename, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
            """, (reference, session["user_id"], category, subject, description, location, image_filename, now, now))
            db.execute("""
                INSERT INTO request_status_history (request_id, old_status, new_status, note, changed_by, created_at)
                VALUES (?, '', 'Pending', 'Request submitted by citizen.', ?, ?)
            """, (cursor.lastrowid, session.get("name", "Citizen"), now))
        flash(f"Request submitted. Keep your reference number: {reference}", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_request.html", categories=CATEGORIES)


@app.route("/requests/<int:request_id>")
@login_required
def request_detail(request_id):
    with get_db() as db:
        item = db.execute("""
            SELECT r.*, u.full_name, u.email
            FROM service_requests r JOIN users u ON u.id = r.user_id
            WHERE r.id = ?
        """, (request_id,)).fetchone()
        history = db.execute(
            "SELECT * FROM request_status_history WHERE request_id = ? ORDER BY id DESC", (request_id,)
        ).fetchall()
    if not item:
        abort(404)
    if session.get("role") != "admin" and item["user_id"] != session["user_id"]:
        abort(403)
    return render_template("request_detail.html", item=item, history=history)


@app.route("/admin")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()[:120]
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = 10
    clauses, params = [], []
    if status_filter in STATUSES:
        clauses.append("r.status = ?")
        params.append(status_filter)
    if search:
        pattern = f"%{search}%"
        clauses.append("(r.reference LIKE ? OR r.subject LIKE ? OR r.location LIKE ? OR r.category LIKE ? OR u.full_name LIKE ? OR u.email LIKE ?)")
        params.extend([pattern] * 6)
    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_db() as db:
        total_filtered = db.execute(
            "SELECT COUNT(*) FROM service_requests r JOIN users u ON u.id = r.user_id" + where_sql,
            params
        ).fetchone()[0]
        pages = max((total_filtered + per_page - 1) // per_page, 1)
        page = min(page, pages)
        rows = db.execute(
            "SELECT r.*, u.full_name, u.email FROM service_requests r JOIN users u ON u.id = r.user_id" +
            where_sql + " ORDER BY r.id DESC LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page]
        ).fetchall()
        stats = {
            "total": db.execute("SELECT COUNT(*) FROM service_requests").fetchone()[0],
            "open": db.execute("SELECT COUNT(*) FROM service_requests WHERE status IN ('Pending', 'In Progress')").fetchone()[0],
            "pending": db.execute("SELECT COUNT(*) FROM service_requests WHERE status='Pending'").fetchone()[0],
            "progress": db.execute("SELECT COUNT(*) FROM service_requests WHERE status='In Progress'").fetchone()[0],
            "resolved": db.execute("SELECT COUNT(*) FROM service_requests WHERE status='Resolved'").fetchone()[0],
        }
    return render_template("admin.html", requests=rows, stats=stats, statuses=STATUSES,
                           status_filter=status_filter, search=search, page=page,
                           pages=pages, total_filtered=total_filtered)


@app.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    with get_db() as db:
        db.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
                   (notification_id, session["user_id"]))
    return redirect(url_for("dashboard"))

@app.route("/admin/requests/<int:request_id>/update", methods=["POST"])
@admin_required
def update_request(request_id):
    status = request.form.get("status", "")
    note = request.form.get("admin_note", "").strip()
    if status not in STATUSES:
        abort(400)
    with get_db() as db:
        row = db.execute("SELECT id, user_id, reference, status FROM service_requests WHERE id = ?", (request_id,)).fetchone()
        if not row:
            abort(404)
        now = datetime.utcnow().isoformat(timespec="seconds")
        db.execute(
            "UPDATE service_requests SET status = ?, admin_note = ?, updated_at = ? WHERE id = ?",
            (status, note, now, request_id)
        )
        if row["status"] != status:
            db.execute(
                "INSERT INTO notifications (user_id, request_id, message, is_read, created_at) VALUES (?, ?, ?, 0, ?)",
                (row["user_id"], request_id,
                 f"Your request {row['reference']} status changed from {row['status']} to {status}.", now)
            )
            db.execute("""
                INSERT INTO request_status_history (request_id, old_status, new_status, note, changed_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (request_id, row["status"], status, note, session.get("name", "Administrator"), now))
    flash("Request updated. The citizen has been notified in their dashboard." if row["status"] != status else "Request details saved.", "success")
    return redirect(url_for("request_detail", request_id=request_id))


@app.errorhandler(413)
def file_too_large(_error):
    return render_template("error.html", code=413, message="The uploaded image is too large. Please choose an image smaller than 5 MB."), 413


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="You do not have permission to view this page."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="The page or request could not be found."), 404


@app.errorhandler(400)
def bad_request(error):
    message = getattr(error, "description", "The request could not be processed.")
    return render_template("error.html", code=400, message=message), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
