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

## Deploy on Render

The **"connection to server at localhost (127.0.0.1) port 5432 failed"** and **"No open ports detected"** errors happen when:

1. **DATABASE_URL** is missing or still `localhost` → the app cannot reach a database on Render (there is no PostgreSQL on the same machine).
2. **Start Command** uses a fixed port (e.g. `8000`) → Render expects the app to listen on **`$PORT`** (e.g. 10000).

### Fix

**1. Add a PostgreSQL database (if you don’t have one)**  
- In Render Dashboard: **New → PostgreSQL**.  
- Create the DB, then open it and copy the **Internal Database URL** (use Internal if the API runs on Render; use External for local or other hosts).

**2. Set environment variables on your Web Service**  
In your service → **Environment** tab, add:

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Paste the **Internal Database URL** from your Render PostgreSQL (e.g. `postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname`) |
| `JWT_SECRET_KEY` | A long random string (e.g. from https://generate-secret.vercel.app/32 or `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Your frontend URL(s), e.g. `https://your-app.onrender.com` or `https://your-vercel-app.vercel.app` |

Do **not** leave `DATABASE_URL` as `postgresql://...@localhost:5432/...`; that only works on your own machine.

**3. Set the Start Command**  
In the Web Service → **Settings** (or **Build & Deploy**) → **Start Command**, use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Use **`$PORT`** so Render can detect the open port.  
- Use **`--host 0.0.0.0`** so the server is reachable from the internet.  
- Omit **`--reload`** in production.

**4. Redeploy**  
Save, then **Manual Deploy → Deploy latest commit** (or push a new commit). The app should start and connect to the Render PostgreSQL.

**5. Run migrations (once)**  
After the first successful deploy, run migrations against the production DB. Either:

- Use **Shell** in the Render dashboard (with the same env as the service), or  
- Locally with `DATABASE_URL` set to the **External** URL:

```bash
export DATABASE_URL="postgresql://...External URL from Render..."
alembic -c alembic.ini upgrade head
```

Optional: the repo includes a **`render.yaml`** Blueprint; you can use **New → Blueprint** and point Render at this repo to create the Web Service and PostgreSQL from the spec.

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
