# Planventure API

A Flask-based REST API for the Planventure trip-planning application. It provides
JWT authentication, per-user trip management (CRUD), a default itinerary
generator, and a health check endpoint — backed by SQLAlchemy with SQLite by
default.

## Tech Stack

- **Flask 2.3** — web framework
- **Flask-SQLAlchemy** — ORM (SQLite by default, any SQLAlchemy URL supported)
- **Flask-JWT-Extended** — JWT access tokens
- **Flask-CORS** — CORS for the React frontend
- **bcrypt** — password hashing
- **email-validator** — email validation
- **python-dotenv** — environment variable loading

## Project Structure

```
planventure-api/
├── app.py              # App factory, CORS, health check, blueprint registration
├── extensions.py       # Shared db (SQLAlchemy) and jwt (JWTManager) instances
├── models.py           # User and Trip models
├── auth_utils.py       # Password hashing + JWT token generation helpers
├── auth_routes.py      # /auth/register and /auth/login
├── auth_middleware.py  # before_request JWT guard for protected routes
├── trip_routes.py      # /trip CRUD blueprint + default itinerary generator
├── init_db.py          # Database table creation script
├── requirements.txt    # Python dependencies
└── instance/           # SQLite database lives here (planventure.db)
```

## Prerequisites

- Python 3.8+
- Git

## Getting Started

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd planventure/planventure-api
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Windows, without activating the venv:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `planventure-api/` directory (make sure `.env` is
listed in `.gitignore`):

```env
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me-too
DATABASE_URL=sqlite:///planventure.db
FRONTEND_URL=http://localhost:3000
```

| Variable         | Default                    | Description                                            |
| ---------------- | -------------------------- | ------------------------------------------------------ |
| `SECRET_KEY`     | `dev`                      | Flask secret key                                       |
| `JWT_SECRET_KEY` | falls back to `SECRET_KEY` | Signing key for JWT tokens                             |
| `DATABASE_URL`   | `sqlite:///planventure.db` | SQLAlchemy database URL                                |
| `FRONTEND_URL`   | `http://localhost:3000`    | Allowed CORS origin(s); comma-separated for multiple   |

### 5. Initialize the database

```bash
python init_db.py
# or on Windows:
.\venv\Scripts\python.exe init_db.py
```

This creates the `users` and `trips` tables (SQLite file at
`instance/planventure.db`).

### 6. Run the server

```bash
flask --app app run --debug --port 5000
# or on Windows:
.\venv\Scripts\python.exe -m flask --app app run --debug --port 5000
```

The API is now available at `http://localhost:5000`.

## Checking If the Server Is Running

### Quick check — hit the health endpoint

**PowerShell:**

```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
```

**curl:**

```bash
curl http://localhost:5000/health
```

A healthy response looks like:

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-10-06T02:52:13.927405+00:00"
}
```

### Check for a process listening on port 5000 (Windows)

```powershell
netstat -ano | Select-String ':5000'
```

To find the actual Python/Flask process:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match 'python' -or $_.CommandLine -match 'flask' } |
  Select-Object ProcessId, Name, CommandLine
```

To stop a server by PID:

```powershell
Stop-Process -Id <PID>
```

### Check on macOS/Linux

```bash
lsof -i :5000
# or
curl -s http://localhost:5000/health
```

## API Reference

All protected routes require the header:

```
Authorization: Bearer <access_token>
```

Obtain a token from `POST /auth/login`.

### Public Endpoints

| Method | Endpoint  | Description                                  |
| ------ | --------- | -------------------------------------------- |
| GET    | `/`       | Welcome message                              |
| GET    | `/health` | Health check (API status + DB connectivity)  |

### Auth

#### `POST /auth/register`

```json
{ "email": "user@example.com", "password": "test1234" }
```

- `201` → `{ "id": 1, "email": "user@example.com" }`
- `400` → invalid/missing email or password (password must be 8–72 bytes)
- `409` → email already registered

#### `POST /auth/login`

```json
{ "email": "user@example.com", "password": "test1234" }
```

- `200` → `{ "access_token": "<jwt>", "token_type": "Bearer" }`
- `401` → invalid credentials

### Trips (protected)

Trips are scoped to the authenticated user — you only ever see your own.

#### `GET /trip`

Returns all trips for the current user:

```json
[
  {
    "id": 1,
    "destination": "Tokyo",
    "start_date": "2026-11-01",
    "end_date": "2026-11-07",
    "latitude": 35.6762,
    "longitude": 139.6503,
    "itinerary": [
      { "date": "2026-11-01", "activities": [] }
    ]
  }
]
```

#### `POST /trip`

```json
{
  "destination": "Tokyo",
  "start_date": "2026-11-01",
  "end_date": "2026-11-07",
  "latitude": 35.6762,
  "longitude": 139.6503
}
```

- `201` → created trip. If `itinerary` is omitted, a default template is
  generated with one entry per day of the trip.
- `400` → validation error (missing fields, bad dates, `end_date` before
  `start_date`, etc.)

#### `GET /trip/<id>`

- `200` → the trip
- `404` → not found (or belongs to another user)

#### `PUT /trip/<id>` / `PATCH /trip/<id>`

`PUT` requires the full payload; `PATCH` accepts partial updates.

- `200` → updated trip
- `400` → validation error
- `404` → not found

#### `DELETE /trip/<id>`

- `204` → deleted (empty body)
- `404` → not found

## Testing with an API Client

The repo includes a Bruno collection under
`collection-veture/planventure-api/` (`registration.yml`, `login.yml`,
`createtrip.yml`, `gettripbyid.yml`, `opencollection.yml`). Open it with the
[Bruno](https://www.usebruno.com/) API client, or use Postman/Insomnia/curl.

Typical flow:

1. `POST /auth/register` — create a user
2. `POST /auth/login` — get an `access_token`
3. `POST /trip` with `Authorization: Bearer <token>` — create a trip
4. `GET /trip/1` — fetch it back

### PowerShell quick test

```powershell
# Register
Invoke-RestMethod -Uri http://localhost:5000/auth/register -Method Post `
  -ContentType 'application/json' `
  -Body '{"email":"user@example.com","password":"test1234"}'

# Login and capture the token
$login = Invoke-RestMethod -Uri http://localhost:5000/auth/login -Method Post `
  -ContentType 'application/json' `
  -Body '{"email":"user@example.com","password":"test1234"}'

# Create a trip
Invoke-RestMethod -Uri http://localhost:5000/trip -Method Post `
  -Headers @{ Authorization = "Bearer $($login.access_token)" } `
  -ContentType 'application/json' `
  -Body '{"destination":"Tokyo","start_date":"2026-11-01","end_date":"2026-11-07"}'

# Get trip by ID
Invoke-RestMethod -Uri http://localhost:5000/trip/1 `
  -Headers @{ Authorization = "Bearer $($login.access_token)" }
```

## Data Models

### User

| Field           | Type         | Notes                    |
| --------------- | ------------ | ------------------------ |
| `id`            | Integer (PK) |                          |
| `email`         | String(255)  | unique, indexed          |
| `password_hash` | String(255)  | bcrypt hash              |
| `created_at`    | DateTime     | UTC                      |
| `updated_at`    | DateTime     | UTC, auto-updated        |

### Trip

| Field         | Type         | Notes                              |
| ------------- | ------------ | ---------------------------------- |
| `id`          | Integer (PK) |                                    |
| `user_id`     | FK → users   | owner                              |
| `destination` | String(255)  | required                           |
| `start_date`  | Date         | ISO format, required               |
| `end_date`    | Date         | must be ≥ `start_date`             |
| `latitude`    | Float        | optional                           |
| `longitude`   | Float        | optional                           |
| `itinerary`   | JSON         | defaults to one entry per trip day |

## CORS

CORS is configured in `app.py` for the React frontend. Allowed origins come
from `FRONTEND_URL` (default `http://localhost:3000`); use a comma-separated
list for multiple origins, e.g.:

```env
FRONTEND_URL=http://localhost:3000,http://localhost:5173
```

Allowed methods: `GET, POST, PUT, PATCH, DELETE, OPTIONS`. Allowed headers:
`Content-Type, Authorization`. Credentials are supported.

## Common Issues

- **No trailing slashes** — routes are registered without them (`/trip`, not
  `/trip/`). A wrong slash can produce 404s or redirects that drop the
  `Authorization` header.
- **401 on protected routes** — check the `Authorization: Bearer <token>`
  header and that the token hasn't expired.
- **`ModuleNotFoundError`** — run commands from the `planventure-api/`
  directory and make sure the venv is active (or use
  `.\venv\Scripts\python.exe` explicitly).
- **"Unknown" endpoint 401s** — `auth_middleware.py` keeps `home`,
  `health_check`, `auth.register`, and `auth.login` public; everything else
  goes through JWT verification.
- **Inspect the database** — install a SQLite viewer VS Code extension and open
  `instance/planventure.db`.

## Next Steps

- More comprehensive input validation and validation error handlers
- Custom error handlers for HTTP exceptions
- Logging configuration
- Database migrations (Flask-Migrate/Alembic)
