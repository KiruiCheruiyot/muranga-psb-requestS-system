# Murang'a County PSB — Public Service Request System

An educational Flask prototype for a mini eCitizen-style public service request portal. Citizens can report issues such as broken streetlights, water supply problems, garbage collection, roads and drainage, and other public service concerns, then track each request until it is resolved.

> **Disclaimer:** This is a student project prototype. It is not an official Murang'a County Government website and is not affiliated with or endorsed by the County. Do not submit real personal or sensitive information.

## Live Demo

- **Live site:** https://muranga-psb-requests-system-1.onrender.com
- **Repository:** https://github.com/KiruiCheruiyot/muranga-psb-requestS-system

> The site runs on a free server. The first visit after inactivity can take about a minute to load, and accounts created while testing may be reset when the server restarts.

## How to Try It

1. Open the live site and click **Create account**.
2. Register as a **Citizen**, sign in, and click **Submit a request**.
3. Open a private window, register as **Administrator (demo)**, and sign in.
4. In the admin dashboard, search for the request, change its status and add a note.
5. Go back to the citizen account to see the new status, the history timeline and the notification.

## Requirements Covered

| Requirement | Where to find it |
|---|---|
| Citizen registration and login | `/register`, `/login` |
| Submit request (category, location, description, optional image) | `/requests/new` |
| Admin dashboard | `/admin` |
| Status tracking (Pending → In Progress → Resolved) | Request detail page and history timeline |
| Basic analytics (open vs resolved cases) | Summary cards on `/admin` |

## Features

- Citizen registration and sign-in with securely hashed passwords
- Submit service requests by category, location, title, and description
- Optional image attachment (PNG, JPG, JPEG, GIF, WEBP; up to 5 MB)
- Unique request reference numbers
- Citizen dashboard with total, pending, in-progress, and resolved summary cards
- Request status history timeline showing submission, status changes, timestamps, administrator name, and notes
- Administrator dashboard with open/resolved analytics
- Administrator status updates and notes
- Admin search across reference, title, category, location, citizen name, and email
- Status filters and paginated admin results (10 requests per page)
- In-app citizen notifications when request status changes, with read/unread state
- CSRF protection on all state-changing forms using a session-bound synchronizer token
- CSRF-protected sign-out via POST, plus access checks so citizens can only view their own requests
- Responsive interface with summary cards, history timeline, and notification centre
- SQLite database for local classroom demonstrations

<!-- Add screenshots to a docs/ folder, then delete the comment markers around this block to show them:

## Screenshots

![Home page](docs/home.png)
![Citizen dashboard](docs/dashboard.png)
![Admin dashboard](docs/admin.png)
![Request detail](docs/request-detail.png)

-->

## Tech Stack

Python 3.11, Flask, SQLite, Jinja2 templates, plain CSS, Gunicorn, hosted on Render.

## Database Tables

`users`, `service_requests`, `notifications`, `request_status_history`

## Requirements

- Python 3.11 or newer
- Windows PowerShell or Command Prompt, or a compatible terminal

## Installation and Local Setup

Open a terminal in the project directory (the folder containing `app.py` and `requirements.txt`) and create a virtual environment:

```bash
python -m venv .venv
```

**Windows Command Prompt (CMD):**

```cmd
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use CMD instead.

## Configure the Administrator and Start the App

Set the environment variables **before the first run**. Choose your own administrator email and a strong, unique password. The app creates an administrator account from these variables if that email does not already exist.

**Windows CMD:**

```cmd
set SECRET_KEY=replace-with-a-long-random-secret-value
set ADMIN_EMAIL=admin@example.com
set ADMIN_PASSWORD=replace-with-a-strong-unique-password
python app.py
```

**Windows PowerShell:**

```powershell
$env:SECRET_KEY="replace-with-a-long-random-secret-value"
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="replace-with-a-strong-unique-password"
python app.py
```

Then open http://127.0.0.1:5000 in your browser. Press `Ctrl+C` in the terminal to stop the server.

> **Demo-only admin sign-up:** For this classroom build, the registration page also lets you choose **Administrator (demo)** so markers can try the admin side. This is intentionally open for demonstration. Anyone can register as an admin, so do not deploy this setup as a real public service website.

Keep `SECRET_KEY` private and use a long random value. Never put real credentials in the README, source code, screenshots, or submission archive.

## Project Structure

```text
muranga_psb_request_system_final/
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
│   ├── new_request.html
│   ├── request_detail.html
│   ├── admin.html
│   └── error.html
└── static/
    ├── style.css
    ├── images/
    │   └── logo.png
    └── uploads/
```

## Testing Checklist

Before presenting, verify these end-to-end flows:

1. Register a citizen account and sign in.
2. Submit a request with all required fields and confirm a unique reference appears.
3. Sign in as an administrator and find the request using search and status filters.
4. Change the request status and add a note.
5. Sign back in as the citizen and confirm the status, history timeline, and notification are visible.
6. Confirm a citizen cannot open another citizen's request or the admin dashboard.
7. Check the layout at desktop and narrow mobile widths, and try an invalid or oversized image upload.

## Image Uploads

Uploaded images are stored in `static/uploads/`. The app limits uploads to 5 MB and checks the filename extension. This is appropriate only for a classroom prototype; extension checks alone are not sufficient for production security. Do not upload private or sensitive documents.

## Deployment Notes

The project includes a `Procfile` for a Python host that supports Flask and Gunicorn (it is deployed on Render). Configure `SECRET_KEY`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` as environment variables in the hosting dashboard, and remove open administrator registration before making the app publicly accessible.

SQLite is suitable for a local classroom prototype, but hosts with ephemeral filesystems (such as Render's free plan) can reset the database after a restart or redeployment. Use a managed database and backups for persistent service.

## Limitations

This prototype is not integrated with county systems, eCitizen, SMS, email, or identity verification. Before real-world use it would need rate limiting, audit logging, secure account recovery, comprehensive upload validation and scanning, accessibility testing, privacy notices, a persistent production database, and authorization to represent the County PSB.

## Author

Enock Kirui. Built as an assessment project.