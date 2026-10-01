# Deployment Guide

This backend will automatically seed the database with exactly 3 team members on every deployment.

## Automatic Deployment

The deployment scripts are configured to:
1. Run database migrations
2. **Delete all existing team members**
3. **Seed exactly 3 team members:**
   - Rohan Shah - Founder & CEO
   - Sonik Lamsal - Co-Founder & CTO
   - Subham Karki - Lead Designer
4. Collect static files

## Platform-Specific Instructions

### Railway
Railway will automatically detect `railway.toml` and run the seed command on every deploy.

1. Connect your GitHub repository to Railway
2. Railway will automatically deploy when you push to main
3. The team data will be reset to exactly 3 members on each deploy

### Render
Render will use `render.yaml` for configuration.

1. Connect your GitHub repository to Render
2. Render will automatically deploy when you push to main
3. The team data will be reset to exactly 3 members on each deploy

### Heroku
Heroku will use the `Procfile` for deployment.

1. Connect your GitHub repository to Heroku
2. Enable automatic deployments from main branch
3. The `release` command in Procfile will run migrations and seed data
4. The team data will be reset to exactly 3 members on each deploy

### Manual Deployment
If deploying manually, run:

```bash
bash deploy.sh
```

Or run commands individually:
```bash
python manage.py migrate
python manage.py seed_content --reset
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

## Environment Variables

Make sure to set these in your hosting platform:

- `SECRET_KEY` - Django secret key (generate a secure one)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your domain name (e.g., `your-app.railway.app`)
- `DATABASE_URL` - PostgreSQL connection string (usually auto-provided)
- `CORS_ALLOWED_ORIGINS` - Your frontend URL (e.g., `https://yoursite.vercel.app`)

## Adding More Team Members

To add more team members in the future:

1. Edit `content/management/commands/seed_content.py`
2. Add new entries to the `TEAM` list
3. Commit and push
4. The deployment will automatically update the database

Or use the Django admin panel at `/admin/` to add team members manually without redeploying.
