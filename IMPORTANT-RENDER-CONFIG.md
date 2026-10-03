# ⚠️ IMPORTANT: Render Configuration

## THE PROBLEM YOU HAD:

Your deployment scripts had `seed_content --reset` which **DELETES ALL DATA** on every deployment!

This is why your team member updates kept disappearing.

## THE FIX:

All deployment files have been updated to NEVER run `--reset` again.

### What Render Actually Uses:

**Build Command:** `./build.sh`
- Installs dependencies
- Runs migrations
- Seeds ONLY if database is empty (first time only)
- Collects static files

**Start Command:** `gunicorn config.wsgi:application`
- Just starts the web server
- NO database operations
- NO seeding

## Files Updated:

### 1. `build.sh` ✅ 
**Correct behavior:**
```bash
python manage.py migrate
python manage.py init_database  # Only seeds if empty!
python manage.py ensure_superuser
```

### 2. `render.yaml` ✅ FIXED
**Before (WRONG):**
```yaml
startCommand: "... && python manage.py seed_content --reset && ..."
```

**After (CORRECT):**
```yaml
buildCommand: "./build.sh"
startCommand: "gunicorn config.wsgi:application"
```

### 3. `Procfile` ✅ FIXED
**Before (WRONG):**
```
release: ... seed_content --reset ...
```

**After (CORRECT):**
```
web: gunicorn config.wsgi:application
```

### 4. `railway.toml` ✅ FIXED
**Before (WRONG):**
```toml
startCommand = "... seed_content --reset ..."
```

**After (CORRECT):**
```toml
startCommand = "gunicorn config.wsgi:application"
```

### 5. `deploy.sh` ✅ DEPRECATED
Marked as deprecated - not used anymore.

---

## Render Dashboard Settings

**⚠️ YOU MUST ALSO CHECK YOUR RENDER DASHBOARD!**

If you manually set the Start Command in Render dashboard, it overrides these files.

### How to Check:

1. Go to https://dashboard.render.com
2. Click your **orik-backend** service
3. Click **"Settings"** tab
4. Scroll to **"Build & Deploy"** section

### What You Should See:

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn config.wsgi:application
```

### If You See Something Else:

**If you see:**
```bash
python manage.py migrate && python manage.py seed_content --reset && ...
```

**DO THIS:**
1. Delete the Start Command (leave it blank to use build.sh)
2. Or change it to: `gunicorn config.wsgi:application`
3. Click **"Save Changes"**
4. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## How It Works Now:

### First Deployment (Fresh Database):
```
✅ Build: Runs migrations
✅ Build: Seeds initial content (3 team members)
✅ Build: Creates superuser
✅ Start: Starts gunicorn
```

### Future Deployments (Database Has Data):
```
✅ Build: Runs migrations (if any)
✅ Build: Checks database - sees content exists
✅ Build: SKIPS seeding (preserves your edits!)
✅ Start: Starts gunicorn
```

---

## Testing:

1. Edit a team member in admin
2. Push any code change to GitHub
3. Wait for Render to redeploy
4. Check admin - **your edit should still be there!** ✅

---

## Summary:

**What was deleting your data:**
- `seed_content --reset` in start commands

**What protects your data now:**
- `init_database` command (only seeds if empty)
- No `--reset` flag anywhere
- Separate build and start phases

**Your data is now safe!** 🎉
