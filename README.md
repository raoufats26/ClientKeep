# ClientKeep — Full Setup & Deployment Guide

---

## 🆕 Phase 2 — What's New

- ✅ Revenue bar chart on dashboard (Chart.js)
- ✅ Activity log (every action is tracked)
- ✅ PDF invoice download (WeasyPrint)
- ✅ Client portal — public link for client to view & confirm payment
- ✅ Reminders system — with overdue detection
- ✅ Profile & password settings page
- ✅ Currency selector (USD, EUR, DZD, and 7 more)
- ✅ Export to CSV (clients + invoices)
- ✅ Recurring invoices (monthly / quarterly)

---

## 📁 Full Folder Structure

```
clientkeep/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
├── Procfile                    ← for Render deployment
├── runtime.txt                 ← for Render deployment
├── .env
├── .gitignore
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── clients.py
│   ├── dashboard.py
│   ├── invoices.py
│   ├── reminders.py
│   ├── settings.py
│   ├── portal.py
│   └── export.py
└── templates/
    ├── base.html
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── dashboard/
    │   └── index.html
    ├── clients/
    │   ├── index.html
    │   ├── form.html
    │   └── view.html
    ├── invoices/
    │   ├── index.html
    │   ├── form.html
    │   ├── view.html
    │   └── pdf_template.html
    ├── reminders/
    │   └── index.html
    ├── settings/
    │   └── index.html
    └── portal/
        └── view.html
```

---

## ⚙️ Local Setup (Phase 2)

### 1 — Install dependencies

```bash
pip install -r requirements.txt
```

WeasyPrint on Windows needs GTK3:
→ Download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
→ Install it, restart terminal, then `pip install WeasyPrint`

### 2 — Run new migrations

```bash
flask db migrate -m "phase2"
flask db upgrade
```

### 3 — Run

```bash
flask run
```

---

## 🚀 Deploy to Render + Neon

### Step 1 — Neon database

1. https://neon.tech → free account → new project `clientkeep`
2. Copy connection string:
   `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`

### Step 2 — Add to your project

Create `Procfile`:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.11.0
```

Create `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
instance/
```

Install gunicorn and freeze:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

Update `config.py` for Neon SSL:
```python
uri = os.environ.get('DATABASE_URL') or 'postgresql://...'
# Fix for Render (postgres:// -> postgresql://)
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
SQLALCHEMY_DATABASE_URI = uri
```

### Step 3 — GitHub

```bash
git init
git add .
git commit -m "ClientKeep"
git remote add origin https://github.com/YOU/clientkeep.git
git push -u origin main
```

### Step 4 — Render

1. render.com → New Web Service → connect GitHub
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn app:app`
4. Env vars:
   - `DATABASE_URL` = your Neon string
   - `SECRET_KEY` = any long random string
   - `FLASK_ENV` = production
5. Deploy → after first deploy, open Shell tab → `flask db upgrade`

---

## 🛟 Troubleshooting

| Problem | Fix |
|---------|-----|
| WeasyPrint fails on Windows | Install GTK3 runtime |
| `No changes detected` on migrate | Check models.py saved, try `flask db stamp head` first |
| Neon SSL error | Add `?sslmode=require` to DATABASE_URL |
| `postgres://` error on Render | Use the config.py fix above |
| Render crash on start | Check logs, ensure SECRET_KEY + DATABASE_URL are set |
