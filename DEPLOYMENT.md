# Primetrade – Deployment Guide

## Build commands

### Backend

```bash
# From project root
pip install -r requirements.txt
python -c "from app.main import app; print('OK')"   # verify import
python -m pytest tests/ -v                          # run tests
uvicorn app.main:app --host 0.0.0.0 --port 8000     # run server (production: no --reload)
```

### Frontend

```bash
# From project root
cd frontend
npm ci
npm run build        # output in frontend/dist
npm run preview      # optional: local preview of production build
```

---

## Environment variables for deployment

### Backend (production)

Set these in your host (e.g. Railway, Render, Fly.io, Docker, or systemd env file). **Do not commit real secrets.**

| Variable | Required | Example / notes |
|----------|----------|------------------|
| `DATABASE_URL` | **Yes** | `postgresql://user:password@host:5432/dbname` (e.g. from managed PostgreSQL) |
| `JWT_SECRET_KEY` | **Yes** | Long random string (e.g. `openssl rand -hex 32`). **Must be different from dev.** |
| `JWT_ALGORITHM` | No | Default: `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default: `30` |
| `CORS_ORIGINS` | **Yes** | Comma-separated frontend origins, e.g. `https://app.example.com,https://www.example.com` |
| `APP_NAME` | No | Default: `Primetrade API` |
| `DEBUG` | No | Set to `false` in production |
| `REDIS_URL` | No | Optional, e.g. `redis://localhost:6379/0` for caching |

**Example (Linux/macOS):**

```bash
export DATABASE_URL="postgresql://u:p@db.example.com:5432/primetrade"
export JWT_SECRET_KEY="your-production-secret-from-openssl-rand-hex-32"
export CORS_ORIGINS="https://your-frontend.vercel.app"
export DEBUG="false"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Frontend (production build)

Set at **build time** (e.g. in CI or your hosting dashboard). Vite embeds `VITE_*` variables into the built JS.

| Variable | Required | Example / notes |
|----------|----------|------------------|
| `VITE_API_URL` | **Yes** | Full backend API base URL, e.g. `https://api.example.com` (no trailing slash) |

**Example (build):**

```bash
export VITE_API_URL="https://api.yourdomain.com"
npm run build
```

Then serve the `frontend/dist` folder with any static host (Nginx, Vercel, Netlify, S3 + CloudFront, etc.).

---

## One-page reference (copy-paste)

**Backend:**

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
APP_NAME=Primetrade API
DEBUG=false
```

**Frontend (build-time):**

```
VITE_API_URL=https://your-backend-api.com
```

---

## Database migrations (production)

After deploying backend, run migrations against the production DB:

```bash
# Ensure DATABASE_URL points to production
alembic -c alembic.ini upgrade head
```

---

## Optional: Docker

**Backend (example):**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run with env file:

```bash
docker build -t primetrade-api .
docker run -p 8000:8000 --env-file .env primetrade-api
```

**Frontend:** Build locally with `VITE_API_URL` set, then serve `dist/` with Nginx or any static server; or use a multi-stage Docker build that runs `npm run build` and serves with Nginx.
