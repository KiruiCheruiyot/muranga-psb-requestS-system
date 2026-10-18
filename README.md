# Murang'a County PSB — Public Service Request System

An educational Flask prototype for a mini eCitizen-style public service request portal. Citizens can report issues such as broken streetlights, water supply problems, garbage collection, roads and drainage, and other public service concerns.

## Features

* Citizen registration and sign-in with securely hashed passwords
* Submit service requests by category, location, title, and description
* Optional image attachment (PNG, JPG, JPEG, GIF, WEBP; up to 5 MB)
* Unique request reference numbers
* Citizen dashboard with total, pending, in-progress, and resolved summary cards
* Citizen dashboard and request tracking
* Request status history timeline showing submission, status changes, timestamps, administrator name, and notes
* Administrator dashboard with open/resolved analytics
* Administrator status updates and notes
* CSRF protection on state-changing forms using a session-bound synchronizer token
* Admin search across reference, title, category, location, citizen name, and email
* Status filters and paginated admin results (10 requests per page)
* In-app citizen notifications when request status changes, with read/unread state
* CSRF-protected sign-out via POST, plus access checks so citizens can only view their own requests
* Responsive interface with refined admin tools, summary cards, request history timeline, and notification centre
* SQLite database for local classroom demonstrations

Requirements

* Python 3.11 or newer
* Windows PowerShell or Command Prompt, or a compatible terminal

Installation and local setup

Open a terminal in the project directory (the folder containing `app.py` and `requirements.txt`). Create and activate a virtual environment:

bash
python -m venv .venv



Windows Command Prompt (CMD):

cmd
.venv\\Scripts\\activate
python -m pip install -r requirements.txt

Windows PowerShell:

powershell
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt



If PowerShell blocks activation, you can use CMD instead; activation is optional if you invoke the virtual environment's Python executable directly.

Configure the administrator and start the app

Set the environment variables **before the first run**. Choose your own administrator email and a strong, unique password. The app can create an administrator account from those variables if that email does not already exist in the database. For this classroom/demo build, the registration page also lets you select “Administrator (demo)” and create an admin account directly. This is intentionally open for demonstration only: anyone can register as an admin, so do not deploy this setup as a real public service website. Keep `SECRET\\\_KEY` private and use a long random value. Do not commit real secrets to GitHub.

 Windows Command Prompt (CMD)

cmd
set SECRET\\\_KEY=replace-with-a-long-random-secret-value
set ADMIN\\\_EMAIL=admin@example.com
set ADMIN\\\_PASSWORD=replace-with-a-strong-unique-password
python app.py


 Windows PowerShell

powershell
$env:SECRET\_KEY="replace-with-a-long-random-secret-value"
$env:ADMIN\_EMAIL="admin@example.com"
$env:ADMIN\_PASSWORD="replace-with-a-strong-unique-password"
python app.py



Keep the secret key and administrator password private. Do not put real credentials in the README, source code, screenshots, or submission archive.

When the server starts, open `http://127.0.0.1:5000` in your browser. Keep the terminal open while using the app; press `Ctrl+C` in the terminal to stop it.

Project structure

text
muranga\_psb\_request\_system\_final/
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── runtime.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── new\_request.html
│   ├── request\_detail.html
│   ├── admin.html
│   └── error.html
└── static/
├── style.css
└── uploads/



Testing checklist

Before presenting, run the app locally and verify these end-to-end flows:

1. Register a citizen account and sign in.
2. Submit a request with all required fields; confirm a unique reference appears.
3. Sign in with an administrator account and find the request using search and status filters.
4. Change the request status and add a note.
5. Sign back in as the citizen and confirm the status, history timeline, and notification are visible.
6. Confirm a citizen cannot open another citizen's request or the admin dashboard.
7. Test the layout at desktop and narrow mobile widths, and try an invalid or oversized image upload.

 Image uploads

Uploaded images are stored in `static/uploads/`. The app limits uploads to 5 MB and checks the filename extension. This is appropriate only for a classroom prototype; filename-extension checks alone are not sufficient for production security. Do not upload private or sensitive documents for demonstrations.

 Deployment notes

The project includes a `Procfile` for a Python hosting service that supports Flask and Gunicorn. For deployment, configure `SECRET\\\_KEY`, `ADMIN\\\_EMAIL`, and `ADMIN\\\_PASSWORD` as environment variables in the hosting dashboard, and disable/remove open administrator registration before making the app publicly accessible. Never commit real credentials. SQLite is suitable for a local classroom/demo prototype, but on hosts with ephemeral filesystems the database may reset after a restart or redeployment. Use a managed database and backups for persistent service.

Important limitations

This is a student project prototype, not an official Murang'a County Government website. It is not integrated with county systems, eCitizen, SMS, email, or identity verification. Do not use it to collect real sensitive personal information. Before real-world use, add rate limiting, audit logging, secure account recovery, comprehensive upload validation/scanning, accessibility testing, privacy notices, a persistent production database, email delivery monitoring if email is added, and authorization to represent the County PSB. CSRF protection is implemented in this demo, but this remains an educational prototype.

