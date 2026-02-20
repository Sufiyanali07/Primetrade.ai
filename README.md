# Primetrade – Full-Stack REST API + React Frontend

A production-ready assignment project: **FastAPI + PostgreSQL + JWT + RBAC** backend and **React + shadcn/ui** frontend.

**→ Step-by-step guide:** see **[STEPS.md](./STEPS.md)** for local setup and Render deployment.

---

## Tech Stack

| Layer   | Technologies |
|--------|---------------|
| Backend | FastAPI, SQLAlchemy ORM, PostgreSQL, Alembic, JWT (PyJWT), Bcrypt, Uvicorn, Pydantic v2 |
| Frontend | React (Vite), TypeScript, shadcn/ui, Tailwind CSS, Axios, React Router, Zustand |
| Testing | pytest, httpx |

---

## API Routes (versioned under `/api/v1`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register user |
| POST | `/api/v1/auth/login` | Public | Login, returns JWT |
| GET | `/api/v1/users` | Admin | List users |
| GET | `/api/v1/products` | Public | List products |
| GET | `/api/v1/products/{id}` | Public | Get product by ID |
| POST | `/api/v1/products` | Admin | Create product |
| PUT | `/api/v1/products/{id}` | Admin | Update product |
| DELETE | `/api/v1/products/{id}` | Admin | Delete product |

- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`

---

## Folder Structure

```
project/
├── app/
│   ├── main.py                 # FastAPI app, CORS, middleware, routes
│   ├── core/
│   │   ├── config.py           # Settings from .env
│   │   ├── security.py         # Bcrypt hash/verify
│   │   └── jwt_handler.py      # JWT create/decode
│   ├── api/
│   │   ├── deps.py             # get_current_user, require_admin
│   │   └── v1/
│   │       ├── routes_auth.py
│   │       ├── routes_users.py
│   │       └── routes_products.py
│   ├── database/
│   │   ├── connection.py       # Engine, Session, get_db
│   │   ├── models.py          # User, Product
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── migrations/        # Alembic
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── product_service.py
│   └── utils/
│       ├── logger.py
│       └── exceptions.py
├── tests/
│   ├── conftest.py            # Fixtures, test client, test user/admin
│   ├── test_auth.py
│   └── test_products.py
├── frontend/                  # Vite + React + shadcn
├── .env.example
├── requirements.txt
├── alembic.ini
├── postman_collection.json
└── README.md
```

---

## Start commands (run both)

Use **two terminals** (backend and frontend run separately).

**Terminal 1 – Backend** (from project root, with venv activated):

```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 – Frontend** (from project root):

```bash
cd frontend
npm run dev
```

- **Backend:** http://localhost:8000 · API docs: http://localhost:8000/api/docs  
- **Frontend:** http://localhost:5173  

---

## How to Run

### Backend

1. **Create a PostgreSQL database** (e.g. `primetrade`).

2. **Copy env and set variables:**
   ```bash
   cp .env.example .env
   # Edit .env: DATABASE_URL, JWT_SECRET_KEY, CORS_ORIGINS
   ```

3. **Create virtualenv and install dependencies:**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Unix: source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run Alembic migrations:**
   ```bash
   alembic -c alembic.ini upgrade head
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Backend: `http://localhost:8000`

### Frontend

1. **From project root:**
   ```bash
   cd frontend
   npm install
   ```

2. **Optional – set API base URL:**
   ```bash
   cp .env.example .env
   # Set VITE_API_URL=http://localhost:8000 (default)
   ```

3. **Start dev server:**
   ```bash
   npm run dev
   ```

Frontend: `http://localhost:5173`

### Give admin role via database query

New registrations get the **user** role only. To make someone an admin, set their role in the database.

**1. Have a user account**  
Register normally via the app (`/register`) or create a user through the API. Note their email.

**2. Connect to your PostgreSQL database**  
Use any client (psql, pgAdmin, DBeaver, etc.) with the same credentials as `DATABASE_URL` in your `.env`.

**3. Run this SQL** (replace the email with the user you want as admin):

```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```

Example:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@gmail.com';
```

**4. Confirm in the database (optional)**

```sql
SELECT id, name, email, role FROM users WHERE email = 'your@email.com';
```

You should see `role = 'admin'`.

**5. Use admin in the app**  
The user must **log out and log in again** so a new JWT is issued with the updated role. After that, they will see admin-only features (e.g. Add product, Edit/Delete products).

---

## Build & test commands

| What | Command |
|------|---------|
| **Backend** – verify app loads | `python -c "from app.main import app; print('OK')"` |
| **Backend** – run tests | `python -m pytest tests/ -v` |
| **Frontend** – install deps | `cd frontend && npm ci` |
| **Frontend** – production build | `cd frontend && npm run build` |
| **Frontend** – preview build | `cd frontend && npm run preview` |

For **deployment** (env vars, production builds, migrations), see **[DEPLOYMENT.md](./DEPLOYMENT.md)**.

---

## Environment Variables

**Backend (`.env`):**

- `DATABASE_URL` – PostgreSQL URL (e.g. `postgresql://user:pass@localhost:5432/primetrade`)
- `JWT_SECRET_KEY` – Secret for signing JWTs (change in production)
- `JWT_ALGORITHM` – Default `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` – Default `30`
- `CORS_ORIGINS` – Comma-separated origins (e.g. `http://localhost:5173`)
- `REDIS_URL` – Optional (stub for future caching)

**Frontend (`.env`):**

- `VITE_API_URL` – Backend base URL (default `http://localhost:8000`)

---

## Alembic Migration Steps

- **Create a new migration:**
  ```bash
  alembic -c alembic.ini revision --autogenerate -m "description"
  ```
- **Apply migrations:**
  ```bash
  alembic -c alembic.ini upgrade head
  ```
- **Rollback one revision:**
  ```bash
  alembic -c alembic.ini downgrade -1
  ```

---

## Testing (Backend)

```bash
# From project root, with venv activated
pip install -r requirements.txt
pytest tests/ -v
```

Uses SQLite by default for tests (`DATABASE_URL` can be overridden).  
Covers: register, login, token validation, RBAC (admin vs user), product CRUD.

---

## Postman

Import `postman_collection.json`. Set collection variable `baseUrl` (e.g. `http://localhost:8000`). After login, set `token` from the login response and use it for protected endpoints.

---

## Scalability Note

- **Stateless API:** JWT allows horizontal scaling; no server-side session store required.
- **Database:** Connection pooling is configured in `app/database/connection.py`; tune `pool_size` and `max_overflow` for load.
- **Caching:** `REDIS_URL` is prepared for optional caching (e.g. product list, JWT blacklist, rate limits).
- **Microservices:** Auth and products can be split into separate services; share JWT validation (same secret/algorithm) or use a small auth service that issues and validates tokens.
- **Load balancing:** Put multiple Uvicorn instances behind a reverse proxy (e.g. Nginx/Traefik); use sticky sessions only if you add stateful components later.

---

## License

Assignment / educational use.
