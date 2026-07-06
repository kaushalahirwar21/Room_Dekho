# Room Dekho

> Find rooms without brokers in Bhopal.

![Room Dekho](https://img.shields.io/badge/Built%20with-Django-green?style=for-the-badge&logo=Django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=Python)
![Database](https://img.shields.io/badge/Database-Vercel%20Postgres-blue?style=for-the-badge&logo=vercel)
![Media](https://img.shields.io/badge/Media%20Storage-Cloudinary-orange?style=for-the-badge&logo=cloudinary)

## Overview

Room Dekho is a modern, broker-free room rental marketplace for Bhopal. It enables seekers to browse verified listings and request bookings directly from owners, and allows owners to post properties and manage requests. The application features email OTP verification, password resets, dynamic search and filters, responsive mobile design, and automatic production database migrations on startup.

## Features

- **Location-based search & filters**: Search properties by location in Bhopal, budget, room type, and occupant preference (bachelors/family).
- **Owner and Seeker Roles**: Dual-user ecosystem.
- **OTP-based Verification**: Secure sign-up and password reset verification using Gmail SMTP.
- **Resilient Booking Requests**: Request to contact owners directly. Booking request email notifications are wrapped in error-handling so that SMTP failures do not block database persistence.
- **Cloud Media Storage**: Automatic routing of uploaded property images to Cloudinary.
- **Responsive Mobile First UI**: Clean layout built with fluid typography (`clamp()`), full-width touch-friendly actions, and compact cards optimized for viewports from 320px to 768px+.
- **Light & Dark Theme**: Premium responsive visual aesthetics.

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Vanilla HTML, CSS, JavaScript (Lucide Icons) |
| Backend | Django 5.0, Django REST Framework, Simple JWT |
| Database | Vercel Postgres (Serverless SQL) |
| Storage | Cloudinary Media Storage |
| Deployment | Vercel Serverless Functions |

## Project Structure

```text
Room Dekho/
|-- accounts/       # User profiles, verification, OTP service, and auth APIs
|-- api/            # Vercel entrypoint WSGI handler and automated startup migrations
|-- bookings/       # Booking requests, owner notifications, and request status APIs
|-- rooms/          # Property listings, image handling, and search/filter APIs
|-- root/           # Core settings, routing, and configurations
|-- static/         # Frontend CSS stylesheets, JS animations/validation, and images
|-- staticfiles/    # Pre-compiled static files committed to Git for Vercel serving
|-- templates/      # Django HTML templates (index, property details, forms, dashboards)
|-- manage.py       # Local Django administration command utility
|-- requirements.txt# Python dependency manifest
|-- vercel.json     # Vercel routing and serverless function build specifications
```

## Getting Started

### Prerequisites

- Python 3.12
- Vercel CLI (optional, for deployment)
- A Cloudinary account (for media storage)
- Vercel Postgres instance (or another Postgres database url)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kaushalahirwar21/Room_Dekho.git
   cd Room_Dekho
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Environment Variables**
   Create a `.env` file by copying the example template:
   ```bash
   copy .env.example .env
   ```

5. **Configure Database & Services**
   Update your local `.env` with your Postgres `DATABASE_URL`, SMTP email credentials, and Cloudinary URL:
   ```env
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   
   # Database (Use SQLite locally by setting USE_SQLITE=True if preferred)
   USE_SQLITE=False
   DATABASE_URL=postgresql://username:password@localhost:5432/room_dekho
   
   # Cloudinary Media Storage (optional locally, falls back to local storage if unset)
   CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
   
   # SMTP Configuration (for OTP verification and alerts)
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

6. **Run Migrations & Compile Assets**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

7. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the local server**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000` in your web browser.

---

## Deployment to Vercel

The application is fully configured for Vercel deployment with automatic migrations executed at runtime.

### 1. Static Asset Strategy
Since Vercel serves serverless functions with a read-only filesystem, Django's static files must be compiled locally using `collectstatic` and committed to your Git repository. The `.gitignore` has been adjusted to allow tracking the `staticfiles/` directory.

### 2. Required Vercel Environment Variables
Add the following variables in the **Vercel Dashboard** under **Project Settings -> Environment Variables**:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Vercel Postgres connection URL (starting with `postgres://`) |
| `CLOUDINARY_URL` | Cloudinary credentials URL (starting with `cloudinary://`) |
| `EMAIL_HOST_USER` | Gmail address for SMTP authentication |
| `EMAIL_HOST_PASSWORD` | App-specific password for Gmail SMTP |
| `SECRET_KEY` | Production Django secret key |
| `DEBUG` | Set to `False` |
| `ALLOWED_HOSTS` | `room-dekho-pied.vercel.app` |
| `CORS_ALLOWED_ORIGINS`| `https://room-dekho-pied.vercel.app` |

*Note: Ensure the value of `CLOUDINARY_URL` starts directly with `cloudinary://` (do not include the prefix `CLOUDINARY_URL=` inside Vercel's value input field).*

---

## API Endpoints

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/signup/` | Register a new user |
| POST | `/api/accounts/verify-otp/` | Verify sign-up OTP |
| POST | `/api/accounts/login/` | Authenticate user & get JWT tokens |
| POST | `/api/accounts/forgot-password/` | Initiate password reset OTP |
| POST | `/api/accounts/reset-password/` | Complete password reset |
| POST | `/api/accounts/test-email/` | Send validation SMTP email |
| GET | `/api/accounts/email-config/` | View current system configuration |
| GET | `/api/accounts/admin/users/` | List all users (Admin only) |
| POST | `/api/accounts/admin/ban-user/{id}/` | Ban/unban user (Admin only) |

### Properties

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/properties/` | Retrieve and filter property list |
| POST | `/api/properties/` | Publish new property (Owner only) |
| GET | `/api/properties/{id}/` | Get detailed property specs |
| DELETE| `/api/properties/admin/delete/{id}/` | Delete property (Admin only) |

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/bookings/request/` | Submit contact request |
| GET | `/api/bookings/my-requests/` | List current user's booking requests |
| PUT | `/api/bookings/update/{id}/` | Update booking status (Owner only) |

---

## Author

**Kaushal Singh Ahirwar**

- Portfolio: [kaushal-port.netlify.app](https://kaushal-port.netlify.app/)
- LinkedIn: [kaushal-singh-ahirwar](https://linkedin.com/in/kaushal-singh-ahirwar)
- GitHub: [Kaushal-Singh-Ahirwar](https://github.com/Kaushal-Singh-Ahirwar)
