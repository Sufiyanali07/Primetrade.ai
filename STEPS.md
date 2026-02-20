# Primetrade – Step-by-step guide

Follow these steps to run the project **locally** and/or **deploy on Render**.

---

## Part 1: Run locally

### 1. Clone and open the project
- Open the project folder in your terminal (and in your editor).

### 2. Backend: Python environment
```bash
# From project root (Primetrade.ai)
python -m venv venv
```
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Then:
```bash
pip install -r requirements.txt
```

### 3. Create a PostgreSQL database
- Install PostgreSQL on your machine (or use a cloud DB).
- Create a database, e.g. `primetrade`.
- Note: host, port (usually 5432), username, password, database name.

### 4. Backend: Environment variables
```bash
# From project root
copy .env.example .env
```
- **Windows:** `copy .env.example .env`
- **Mac/Linux:** `cp .env.example .env`

Open `.env` and set at least:
- **DATABASE_URL** = `postgresql://USER:PASSWORD@localhost:5432/primetrade` (use your DB user, password, and DB name).
- **JWT_SECRET_KEY** = any long random string (e.g. from https://generate-secret.vercel.app/32).
- **CORS_ORIGINS** = `http://localhost:5173` (for the frontend).

Save the file.

### 5. Run database migrations
```bash
# From project root, with venv activated
alembic -c alembic.ini upgrade head
```

### 6. Start the backend
```bash
# From project root, with venv activated
uvicorn app.main:app --reload --port 8000
```
- API: http://localhost:8000  
- Docs: http://localhost:8000/api/docs  

Leave this terminal open.

### 7. Frontend: Install and run
Open a **second terminal**. From project root:

```bash
cd frontend
npm install
npm run dev
```
- App: http://localhost:5173  

### 8. Create an admin user (optional)
- Register once at http://localhost:5173/register.
- Then in your PostgreSQL client (psql, pgAdmin, DBeaver, etc.) run:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```
- Log out and log in again in the app to get admin features.

---

## Part 2: Deploy on Render

### 1. Push your code to GitHub
- Create a repo and push this project (ensure `.env` is in `.gitignore`; only `.env.example` should be committed).

### 2. Create a PostgreSQL database on Render
- Go to https://dashboard.render.com.
- **New +** → **PostgreSQL**.
- Create the database (e.g. name: `primetrade-db`).
- After creation, open it and copy the **Internal Database URL** (you’ll use it in the next part).

### 3. Create a Web Service on Render
- **New +** → **Web Service**.
- Connect your GitHub repo and select this project.
- Configure:
  - **Name:** e.g. `primetrade-api`
  - **Runtime:** Python
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Set environment variables (Render Web Service)
In the Web Service → **Environment** tab, add:

| Key | Value |
|-----|--------|
| **DATABASE_URL** | Paste the **Internal Database URL** from your Render PostgreSQL (Step 2). |
| **JWT_SECRET_KEY** | A long random string (e.g. from https://generate-secret.vercel.app/32). |
| **CORS_ORIGINS** | Your frontend URL, e.g. `https://your-frontend.onrender.com` or `https://your-app.vercel.app`. |

Do **not** use `localhost` for `DATABASE_URL` on Render.

### 5. Deploy
- Click **Create Web Service** (or **Save** if you already created it).
- Wait for the build and deploy to finish.

### 6. Run migrations on production (one time)
After the first successful deploy:

- Open your Web Service on Render.
- Go to **Shell** (or use a one-off job if you prefer).
- Run (Render injects env vars, so `DATABASE_URL` is already set):
```bash
alembic -c alembic.ini upgrade head
```

Alternatively, run the same command **on your machine** with `DATABASE_URL` set to the **External** database URL from Render (so it connects to the cloud DB).

### 7. (Optional) Deploy the frontend
- Deploy the `frontend` folder to Vercel, Netlify, or another host.
- Set **VITE_API_URL** at build time to your Render API URL, e.g. `https://primetrade-api.onrender.com`.
- In Render, set **CORS_ORIGINS** to that frontend URL (e.g. `https://your-app.vercel.app`).

---

## Quick reference

| Task | Command |
|------|--------|
| Backend (local) | `uvicorn app.main:app --reload --port 8000` |
| Frontend (local) | `cd frontend && npm run dev` |
| Migrations (local) | `alembic -c alembic.ini upgrade head` |
| Migrations (Render) | In Render Shell: `alembic -c alembic.ini upgrade head` |
| Make user admin | `UPDATE users SET role = 'admin' WHERE email = '...';` |

If something fails, check:
- **DATABASE_URL** is set (in `.env` locally, in Render Environment on production).
- Migrations were run (`alembic upgrade head`).
- Start command on Render uses `$PORT`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
