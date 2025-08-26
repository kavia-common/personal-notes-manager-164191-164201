# Notes Backend (FastAPI)

This service exposes a RESTful API for managing personal notes backed by a MySQL database.

## Environment Variables
The application reads database configuration from environment variables. These must be provided by the orchestrator and set in the container's `.env` file.

- MYSQL_URL: Optional full SQLAlchemy DSN (e.g., `mysql+pymysql://user:pass@host:3306/dbname`). If provided, it takes precedence.
- MYSQL_USER: MySQL username (required if `MYSQL_URL` is not provided)
- MYSQL_PASSWORD: MySQL password (required if `MYSQL_URL` is not provided)
- MYSQL_DB: MySQL database name (required if `MYSQL_URL` is not provided)
- MYSQL_PORT: MySQL TCP port (optional; defaults to `3306`)

Note: The host defaults to `localhost` when `MYSQL_URL` is not provided. If your environment uses a different hostname, supply the full `MYSQL_URL`.

## Running
- Install dependencies from `requirements.txt`.
- Start the app with `uvicorn src.api.main:app --host 0.0.0.0 --port 3001` (recommended to match frontend default)
  - Or set your preferred port; ensure the frontend `REACT_APP_API_BASE_URL` matches.

## CORS
- Configure allowed origins using environment variable `ALLOWED_ORIGINS` (comma-separated).
  - Defaults to `http://localhost:3000,http://127.0.0.1:3000`.
- Example:
  ```
  ALLOWED_ORIGINS=http://localhost:3000
  ```

## API
Interactive docs are available at `/docs` and `/redoc`.

### Endpoints
- GET `/` – Health Check
- GET `/notes` – List all notes
- POST `/notes` – Create a new note
- GET `/notes/{id}` – Get a note by ID
- PUT `/notes/{id}` – Update a note
- DELETE `/notes/{id}` – Delete a note

## Migrations
This service automatically creates the `notes` table if it doesn't exist on startup using SQLAlchemy metadata. For production systems, consider using Alembic migrations.
