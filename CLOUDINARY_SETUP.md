# Cloudinary Setup Guide

## ✅ Cloudinary is Now Configured!

All uploaded images will be stored permanently in Cloudinary cloud storage.

---

## 🔑 Your Cloudinary Credentials

Based on what you provided:
- **Cloud Name:** `IUG9iZaGxneyU8xeMpaLzgIt4QY`  
- **API Key:** `328543825699688`
- **API Secret:** (You should have this from Cloudinary dashboard)

---

## 📋 Setup Steps for Render

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com

### 2. Select Your Backend Service
Click on "orik-backend" (or your backend service name)

### 3. Go to Environment Variables
Click on the **"Environment"** tab in the left sidebar

### 4. Add Cloudinary Variables
Click **"Add Environment Variable"** and add these three:

**Variable 1:**
- Key: `CLOUDINARY_CLOUD_NAME`
- Value: `IUG9iZaGxneyU8xeMpaLzgIt4QY`

**Variable 2:**
- Key: `CLOUDINARY_API_KEY`
- Value: `328543825699688`

**Variable 3:**
- Key: `CLOUDINARY_API_SECRET`
- Value: `[Your API Secret from Cloudinary dashboard]`

### 5. Save Changes
Click **"Save Changes"** button at the bottom

### 6. Redeploy
Render will automatically redeploy your service

---

## 🎯 What Happens Now

### In Production (Render):
✅ All uploaded images → Stored in Cloudinary
✅ Images persist forever (never deleted on restart)
✅ Fast CDN delivery worldwide
✅ Automatic image optimization

### In Development (Local):
✅ Images stored locally in `media/` folder
✅ No Cloudinary charges during development

---

## 🔍 How to Find Your API Secret

If you don't have the API Secret:

1. Go to https://cloudinary.com
2. Log in to your account
3. Go to **Dashboard**
4. You'll see:
   - Cloud Name: `IUG9iZaGxneyU8xeMpaLzgIt4QY`
   - API Key: `328543825699688`
   - API Secret: `[Click the eye icon to reveal]`

---

## ✅ Testing

After adding environment variables and redeploying:

1. Go to: https://orik-backend.onrender.com/admin/
2. Log in to admin panel
3. Go to **Team members**
4. Upload a new photo for a team member
5. Save
6. Check your frontend - the image should appear!
7. Restart your Render service - the image will still be there! 🎉

---

## 💡 Additional Notes

- **Free Tier:** Cloudinary free tier includes 25GB storage and 25GB bandwidth/month
- **Automatic Optimization:** Images are automatically optimized for web delivery
- **Backup:** Your default team photos are still in the repository as fallback
- **CDN:** Images are served from Cloudinary's global CDN for fast loading

---

## 🚀 After Setup is Complete

Your team members can upload images via admin panel and they will:
1. ✅ Upload to Cloudinary cloud
2. ✅ Be accessible via Cloudinary CDN URLs
3. ✅ Persist forever (even after restarts)
4. ✅ Load fast worldwide
