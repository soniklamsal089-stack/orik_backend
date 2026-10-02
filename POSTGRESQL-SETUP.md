# PostgreSQL Setup for Production

## Why PostgreSQL?

SQLite is file-based and gets deleted on every Render deployment. PostgreSQL is a separate database service that persists your data permanently.

## Setup Steps

### 1. PostgreSQL Database (Already Done ✓)

You already have a PostgreSQL database on Render:
- **Name:** orik-db
- **Database:** orik
- **Username:** orik
- **Region:** Oregon (US West)
- **Internal URL:** `postgresql://orik:EjN9q2tmgUE9MjULAdU6W9GdvIW600Z4@dpg-dar9oim0tbcc739iiu0g-a/orik`

### 2. Environment Variable (Already Done ✓)

Your backend service already has:
- **Key:** `DATABASE_URL`
- **Value:** `postgresql://orik:EjN9q2tmgUE9MjULAdU6W9GdvIW600Z4@dpg-dar9oim0tbcc739iiu0g-a/orik`

Django automatically uses PostgreSQL when `DATABASE_URL` is set (see `config/settings.py`).

### 3. Automatic Initialization

The `build.sh` script now automatically:
1. ✓ Runs migrations (`python manage.py migrate`)
2. ✓ Seeds initial content ONLY if database is empty (`python manage.py init_database`)
3. ✓ Creates superuser if environment variables are set (`python manage.py ensure_superuser`)

**This means:**
- First deployment: Database is seeded with 3 default team members
- Future deployments: **Your edits are preserved!** ✓

## How It Works

### build.sh
Runs on every Render deployment:
```bash
python manage.py migrate              # Apply database schema changes
python manage.py init_database        # Seed only if empty (safe!)
python manage.py ensure_superuser     # Create admin user if needed
```

### init_database command
Smart seeding that checks if data exists:
```python
if TeamMember.objects.count() > 0:
    print("✓ Database already has content - skipping seed")
    # Preserves your admin edits!
else:
    print("Database is empty - seeding initial content...")
    # First deployment only
```

## Verifying It Works

### Test 1: Edit Team Member
1. Go to admin: https://orik-backend.onrender.com/admin/
2. Edit a team member (change name, role, etc.)
3. Save

### Test 2: Deploy and Check
1. Make any code change and push to GitHub
2. Wait for Render to deploy (3-5 minutes)
3. Check admin → Team members
4. **Your edit should still be there!** ✓

## Troubleshooting

### Problem: Team members still reset

**Check:**
1. Is `DATABASE_URL` set in Render environment variables?
2. Does it start with `postgresql://` (not `sqlite`)?
3. Check deployment logs - does it say "Database already has content"?

**Fix:**
If logs show "Database is empty" on every deploy, the PostgreSQL connection might not be working.

### Problem: Can't log into admin

**Solution:**
Run in Render Shell:
```bash
python manage.py ensure_superuser
```

Or set environment variables:
- `DJANGO_SUPERUSER_USERNAME=admin`
- `DJANGO_SUPERUSER_EMAIL=admin@orikwebcraft.com`
- `DJANGO_SUPERUSER_PASSWORD=your_secure_password`

## Cost

- **PostgreSQL Free Tier:** 1GB storage, expires after 90 days
- **After 90 days:** $7/month (or create a new free database)

## Local Development

Local development still uses SQLite (`db.sqlite3`):
```bash
python manage.py migrate
python manage.py seed_content
python manage.py createsuperuser
```

To use PostgreSQL locally, set `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://localhost/orik_dev
```
