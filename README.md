# JWT Auth Service

A production-style authentication and authorization microservice built with FastAPI, featuring JWT-based login, role-based access control (RBAC), and refresh tokens — fully containerized and tested.

## Features

- User signup with bcrypt password hashing
- Login issuing short-lived access tokens and long-lived refresh tokens (JWT)
- Role-based access control (`user` / `admin`)
- Protected routes via FastAPI dependency injection
- Token refresh flow without re-authentication
- Automated test suite (pytest) covering success and failure paths
- Fully containerized with Docker Compose (app + database + test database)
- CI pipeline via GitHub Actions running tests on every push

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| Auth | OAuth2PasswordBearer, JWT (python-jose) |
| Password hashing | passlib + bcrypt |
| ORM / Database | SQLAlchemy 2.0, PostgreSQL 16 |
| Testing | pytest, httpx, FastAPI TestClient |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |

## Running the project

**Requirements:** Docker Desktop installed and running.

\`\`\`bash
git clone https://github.com/Krishnaofficl/jwt-auth-service.git
cd jwt-auth-service
docker compose up --build -d
\`\`\`

Once running, visit **http://127.0.0.1:8000/docs** for interactive API documentation (Swagger UI).

## Running tests

\`\`\`bash
pytest -v
\`\`\`

## API Endpoints

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/health` | Health check | No |
| POST | `/auth/signup` | Create a new user | No |
| POST | `/auth/login` | Login, returns access + refresh tokens | No |
| POST | `/auth/refresh` | Exchange refresh token for new access token | No |
| GET | `/users/me` | Get current logged-in user | Yes |
| GET | `/admin/dashboard` | Admin-only route | Yes (admin role) |

## Example: Signup and Login

\`\`\`bash
curl -X POST http://127.0.0.1:8000/auth/signup \\
  -H "Content-Type: application/json" \\
  -d '{"email": "test@example.com", "password": "mypassword123"}'

curl -X POST http://127.0.0.1:8000/auth/login \\
  -d "username=test@example.com&password=mypassword123"
\`\`\`

## Architecture

Client → FastAPI (Auth Router / Users Router) → Security Layer (JWT + OAuth2) → SQLAlchemy ORM → PostgreSQL