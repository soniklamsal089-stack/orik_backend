# Syncing Production Data to Local Development

This guide explains how to sync your production database data (team members, projects, testimonials, site settings) to your local development environment.

## Prerequisites

- Local backend server running on SQLite or local PostgreSQL
- Production backend deployed and accessible at https://orik-backend.onrender.com

## Method 1: Sync from Production API (Recommended)

This method fetches data from your production API endpoints and saves it locally.

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py sync_from_api
```

### Custom API URL

If your production URL is different:

```powershell
.\.venv\Scripts\python.exe manage.py sync_from_api --api-url=https://your-backend.com/api
```

## Method 2: Sync from Production Database (Direct)

If you have direct access to the production PostgreSQL database:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py sync_from_production --production-url="postgresql://user:password@host/database"
```

**Note:** This requires the production database to allow external connections and `psycopg2-binary` package installed.

## What Gets Synced

✅ **Team Members** - All team member profiles with photos, contact info, and social links  
✅ **Projects** - Your portfolio projects with descriptions and details  
✅ **Testimonials** - Client testimonials and reviews  
✅ **Site Settings** - Contact information, social links, site metadata  

## Troubleshooting

### Production API Returns 500 Error

The production server might have outdated code or database issues. Deploy the latest code:

1. Push your local changes to GitHub:
   ```powershell
   git add .
   git commit -m "Fix seed data and deployment scripts"
   git push origin main
   ```

2. Render will auto-deploy and run the fixed `init_database` command

3. Wait for deployment to complete, then retry the sync

### Connection Timeouts

Render free tier services may spin down when inactive. Try:

1. Visit https://orik-backend.onrender.com/api/content/ in your browser to wake it up
2. Wait 30-60 seconds for the server to start
3. Retry the sync command

### Missing Data After Sync

Check that your local database is not read-only and you have write permissions:

```powershell
# Check local database file
ls backend\db.sqlite3

# Verify data was synced
.\.venv\Scripts\python.exe manage.py shell
>>> from content.models import TeamMember
>>> TeamMember.objects.count()
>>> TeamMember.objects.all()
```

## Workflow

**Typical development workflow:**

1. **Edit in Production**: Make changes via Render admin panel at https://orik-backend.onrender.com/admin/
2. **Sync to Local**: Run `python manage.py sync_from_api` to get the latest data locally
3. **Develop Locally**: Test features with real production data
4. **Deploy Changes**: Push code changes (not data) to GitHub → Render auto-deploys
5. **Data Persists**: Your production edits survive the deployment (no reset!)

## Frequency

- **Weekly**: Sync when you add new team members or update contact info in production
- **On Demand**: Sync when you need fresh production data for local testing
- **After Production Edits**: Always sync after making changes in production admin

