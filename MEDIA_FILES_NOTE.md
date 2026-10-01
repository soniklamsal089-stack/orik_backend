# Media Files Configuration

## Current Issue
Uploaded images (team photos) are not persisting on Render because Render uses **ephemeral storage**.

## What This Means
- Images uploaded via admin panel are stored temporarily
- When the service restarts/redeploys, all uploaded images are **deleted**
- The database still has the file paths, but the actual files are gone

## Solutions

### Option 1: Use Cloud Storage (Recommended for Production)

#### Cloudinary (Easiest)
1. Sign up at https://cloudinary.com (free tier available)
2. Install: `pip install cloudinary django-cloudinary-storage`
3. Add to `requirements.txt`:
   ```
   cloudinary>=1.41
   django-cloudinary-storage>=0.3
   ```
4. Add to `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'cloudinary_storage',
       'cloudinary',
       ...
   ]
   
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': env('CLOUDINARY_API_KEY'),
       'API_SECRET': env('CLOUDINARY_API_SECRET')
   }
   
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```
5. Set environment variables in Render

#### AWS S3
1. Create S3 bucket
2. Install: `pip install boto3 django-storages`
3. Configure in settings.py
4. Set AWS credentials in environment variables

### Option 2: Render Disk (Persistent Storage)
Render offers persistent disk storage (paid feature)
- Go to your service dashboard
- Add a persistent disk
- Mount it to `/opt/render/project/src/media`

### Option 3: Use Default Photos (Current Workaround)
For testing, commit team photos to the repo:
1. Place photos in `backend/media/team/`
2. Commit them to git
3. Update seed_content.py to use these committed photos

## Current Configuration
- Media files are served via Django URLs
- MEDIA_ROOT = BASE_DIR / "media"
- MEDIA_URL = "media/"
- Files are stored locally but will be lost on restart
