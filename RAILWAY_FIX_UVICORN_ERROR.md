# Fix: Railway "uvicorn: command not found" Error

## Problem

Railway tried to start the application before installing dependencies, resulting in:
```
/bin/bash: line 1: uvicorn: command not found
```

## Root Cause

Railway's Railpack detected Python but didn't find a proper build configuration, so it tried to run the start command without installing `requirements.txt` first.

## Solution: Use Railway Dashboard (Fastest - 2 minutes)

### Step 1: Go to Railway Dashboard

Open your project:
```
https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
```

### Step 2: Delete Failed Service

1. Click on the service "focused-motivation"
2. Go to **Settings** tab
3. Scroll to bottom
4. Click **"Delete Service"**
5. Confirm deletion

### Step 3: Redeploy with GitHub

**Option A: GitHub Integration (Recommended)**

1. First, push all files to GitHub:
   ```bash
   cd /mnt/d/Dev2/code-review-engine
   git add Dockerfile railway.json requirements.txt Procfile nixpacks.toml src/api/
   git commit -m "Add Railway deployment with all configs"
   git push origin main
   ```

2. In Railway dashboard:
   - Click **"+ New"**
   - Select **"GitHub Repo"**
   - Choose your repository: `code-review-engine`
   - Select branch: `main`
   - Railway will auto-build

3. Railway will now:
   - ✅ Install requirements.txt (includes uvicorn)
   - ✅ Use Procfile for start command
   - ✅ Build successfully

**Option B: Railway CLI (Alternative)**

If you prefer CLI, open a regular PowerShell/CMD:

```powershell
cd /mnt/d/Dev2/code-review-engine
railway up
```

## Files Created to Fix This

I've created three configuration files that will ensure proper build:

### 1. `Procfile` ✅
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```
Tells Railway how to start the app.

### 2. `nixpacks.toml` ✅
```toml
[phases.setup]
nixPkgs = ["python311", "gcc", "git"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
```
Explicitly defines build phases (setup → install → start).

### 3. Updated `railway.json` ✅
Now includes explicit start command.

## Verification After Redeployment

### 1. Check Build Logs

In Railway dashboard:
- Click on your service
- Go to **"Deployments"** tab
- Click on latest deployment
- View build logs

You should see:
```
✓ Installing requirements.txt
✓ Successfully installed uvicorn fastapi ...
✓ Starting application
```

### 2. Test Health Endpoint

Once deployed, get your URL from Railway dashboard and test:

```bash
curl https://YOUR-SERVICE-URL.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T...",
  "service": "autorev-api"
}
```

### 3. View API Docs

Open in browser:
```
https://YOUR-SERVICE-URL.up.railway.app/docs
```

You should see the interactive Swagger UI.

## Alternative: Force Dockerfile Build

If you want Railway to use the Dockerfile instead of auto-detection:

### In Railway Dashboard:

1. Click on your service
2. Go to **Settings** tab
3. Find **"Build"** section
4. Change **Builder** to **"Dockerfile"**
5. Set **Dockerfile Path** to `Dockerfile`
6. Click **Save**
7. Click **"Redeploy"** button

This forces Railway to use your Dockerfile, which has all dependencies properly configured.

## Summary of What Changed

### Before (Failed):
- Railway auto-detected Python
- Tried to run start command immediately
- No dependencies installed → uvicorn not found

### After (Will Work):
- `Procfile` tells Railway the start command
- `nixpacks.toml` defines build phases
- Railway installs `requirements.txt` BEFORE starting
- uvicorn is available when start command runs

## Expected Timeline

1. **Delete old service**: 10 seconds
2. **Push to GitHub**: 1 minute
3. **Redeploy from GitHub**: 2-3 minutes
4. **Test endpoints**: 30 seconds

**Total**: ~5 minutes to working API

## Quick Commands

```bash
# Push changes to GitHub
cd /mnt/d/Dev2/code-review-engine
git add .
git commit -m "Fix Railway deployment configuration"
git push origin main

# Then in Railway dashboard, deploy from GitHub
```

## Need Help?

If redeployment still fails:

1. **Check build logs** in Railway dashboard
2. **Verify requirements.txt** has `uvicorn[standard]>=0.27.0`
3. **Try Dockerfile builder** instead of auto-detection
4. **Share error message** for specific help

---

**Next Step**: Delete the failed service and redeploy using GitHub integration (most reliable method).
