# Room Dekho

> Find rooms without brokers in Bhopal.

![Room Dekho](https://img.shields.io/badge/Built%20with-Django-green?style=for-the-badge&logo=Django)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=Python)
![Database](https://img.shields.io/badge/Database-Supabase%20Postgres-3ECF8E?style=for-the-badge&logo=Supabase)

## Overview

Room Dekho is a Django-based rental marketplace for Bhopal. It helps seekers find rooms directly from owners without brokerage and includes authentication, listings, booking flows, and a live Vercel deployment backed by Supabase PostgreSQL.

## Features

- Location-based room search
- Price filtering
- Property listing and detail pages
- Owner and seeker roles
- OTP-based signup and verification
- Login and password reset APIs
- Light and dark mode UI
- Responsive frontend

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Django, Django REST Framework, JWT |
| Database | Supabase PostgreSQL |
| Deployment | Vercel |

## Getting Started

### Prerequisites

- Python 3.10 or newer
- A Supabase Postgres database or another Postgres-compatible `DATABASE_URL`

### Installation

1. Clone the repository

```bash
git clone https://github.com/kaushalahirwar21/Room_Dekho.git
cd Room\ Dekho
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create your local env file

```bash
copy .env.example .env
```

5. Update `.env` with your database and email credentials

6. Run migrations

```bash
python manage.py migrate
```

7. Create a superuser

```bash
python manage.py createsuperuser
```

8. Start the server

```bash
python manage.py runserver
```

9. Open `http://127.0.0.1:8000`

## Environment Variables

Example:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
USE_SQLITE=False
DATABASE_URL=postgresql://username:password@host:5432/postgres

ALLOWED_HOSTS=localhost,127.0.0.1,room-dekho-pied.vercel.app
CORS_ALLOWED_ORIGINS=https://room-dekho-pied.vercel.app

EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
```

Notes:

- Use `DATABASE_URL` for Supabase or any hosted Postgres database.
- `USE_SQLITE=True` can still be used for local fallback development if needed.
- Do not commit your real `.env` file.

## API Endpoints

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/signup/` | Register a user |
| POST | `/api/accounts/verify-otp/` | Verify OTP |
| POST | `/api/accounts/login/` | Login user |
| POST | `/api/accounts/forgot-password/` | Send reset OTP |
| POST | `/api/accounts/reset-password/` | Reset password |

### Properties

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/properties/` | List properties |
| POST | `/api/properties/` | Create property |
| GET | `/api/properties/{id}/` | Property details |

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/bookings/request/` | Request booking |
| GET | `/api/bookings/list/` | List bookings |

## User Roles

| Role | Permissions |
|---|---|
| Seeker | Browse listings and request bookings |
| Owner | Create listings and manage bookings |
| Admin | Full access |

## Deployment

### Vercel

This project is deployed on Vercel and uses Supabase PostgreSQL in production.

Set these values in Vercel Project Settings -> Environment Variables:

```env
DATABASE_URL=postgresql://username:password@host:6543/postgres
DEBUG=False
ALLOWED_HOSTS=room-dekho-pied.vercel.app
CORS_ALLOWED_ORIGINS=https://room-dekho-pied.vercel.app
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
SECRET_KEY=your-secret-key
```

After that, deploy from GitHub or with:

```bash
vercel --prod
```

### Supabase

Use the pooled Postgres connection string from Supabase for production deployments.

## Project Structure

```text
Room Dekho/
|-- accounts/
|-- api/
|-- bookings/
|-- rooms/
|-- root/
|-- static/
|-- templates/
|-- manage.py
|-- requirements.txt
|-- vercel.json
```

## Screenshots

### Light Mode

![Light Mode](static/images/bhopal-light.png)

### Dark Mode

![Dark Mode](static/images/bhopal_dark.png)

## Live Demo

https://room-dekho-pied.vercel.app/

## Author

**Kaushal Singh Ahirwar**

- Portfolio: https://kaushal-port.netlify.app/
- LinkedIn: https://linkedin.com/in/kaushal-singh-ahirwar
- GitHub: https://github.com/Kaushal-Singh-Ahirwar
