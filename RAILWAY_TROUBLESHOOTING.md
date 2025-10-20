# Railway Deployment Troubleshooting Guide

## Current Status

❌ **URL still returns 404**: `https://authentic-nurturing-production.up.railway.app/health`

```json
{"status":"error","code":404,"message":"Application not found"}
```

## All Fixes Applied

✅ **railway.json** - Fixed hardcoded startCommand (was the root cause)
✅ **nixpacks.toml** - Proper Python module start
✅ **Procfile** - Backup start command
✅ **src/api/main.py** - Reads PORT from environment
✅ **start.sh** - Backup startup script

All changes pushed to GitHub: https://github.com/dbbuilder/AI-code-review

## Why You're Still Seeing 404

The 404 "Application not found" from Railway means:

### Option 1: Service Hasn't Been Redeployed
- Railway needs to pull the latest code and rebuild
- If GitHub auto-deploy isn't connected, you need to manually trigger redeploy
- **Action**: Go to Railway dashboard and click "Redeploy"

### Option 2: Service Doesn't Exist or Wrong URL
- The service "authentic-nurturing" might have been deleted
- The URL might have changed
- **Action**: Verify the service exists and get the correct URL

### Option 3: GitHub Auto-Deploy Not Connected
- Railway isn't automatically deploying when you push to GitHub
- **Action**: Connect GitHub repo in Railway settings

## Step-by-Step: Redeploy from Railway Dashboard

### 1. Open Railway Dashboard
```
https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
```

### 2. Check Services List
You should see services in your project. Look for:
- "authentic-nurturing" (the old service name)
- Any other services

**If you don't see any services**:
- The service was deleted or never created
- You need to create a new service (see Section: Create New Service)

### 3. Click on the Service
Click on "authentic-nurturing" (or whatever service name you see)

### 4. Check Latest Deployment
- Go to **"Deployments"** tab
- Look at the most recent deployment
- Check the **status**: Active, Failed, Building, etc.
- Check the **timestamp**: When was it last deployed?

**If last deployment is BEFORE your latest git push**:
- Railway hasn't picked up your changes
- GitHub auto-deploy might not be connected

### 5. View Deployment Logs
- Click on the latest deployment
- Click **"View Logs"**
- Look for errors:
  - `Error: Invalid value for '--port': '$PORT'` = Old config still being used
  - `ModuleNotFoundError` = Python import issues
  - `Port already in use` = Port conflict
  - Build success but crash on start = Check startup logs

### 6. Manually Redeploy
- Go to **"Settings"** tab
- Scroll down to **"Service Settings"**
- Click **"Redeploy"** button
- Wait for build to complete (2-3 minutes)

### 7. Verify Build Configuration
While waiting, check:

**Settings → Build**:
- **Builder**: Should be "Nixpacks" (not Dockerfile)
- **Root Directory**: Should be `/` or empty
- **Build Command**: Should be empty (nixpacks handles it)

**Settings → Deploy**:
- **Start Command**: Should be `python -m src.api.main`
- Or empty (will use railway.json)

### 8. Get the Correct Public URL
After deployment:
- Go to **"Settings"** → **"Networking"**
- Under **"Public Networking"**, you'll see the domain
- It might be different from `authentic-nurturing-production.up.railway.app`
- Copy the exact URL shown

### 9. Test the New URL
```bash
curl https://YOUR-ACTUAL-URL.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T12:34:56.789Z",
  "service": "autorev-api"
}
```

## Option B: Create New Service (If Old One Is Gone)

If "authentic-nurturing" service doesn't exist:

### 1. Create New Service from GitHub
- In Railway project, click **"+ New"**
- Select **"GitHub Repo"**
- Choose repository: `dbbuilder/AI-code-review`
- Select branch: `master`
- Click **"Deploy"**

### 2. Railway Auto-Detection
Railway will automatically:
- Detect Python project
- Use Nixpacks builder
- Read railway.json configuration
- Install dependencies from requirements.txt
- Start with command from railway.json

### 3. Wait for Build
- Monitor build logs in real-time
- Look for:
  ```
  ✓ Installing requirements.txt
  ✓ Successfully installed fastapi uvicorn ...
  ✓ Starting application
  ✓ Application startup complete
  ```

### 4. Generate Public Domain
- Go to new service **Settings** → **Networking**
- Click **"Generate Domain"**
- Railway will create a URL like: `service-name-production.up.railway.app`
- Copy this URL

### 5. Test Health Endpoint
```bash
curl https://NEW-URL.up.railway.app/health
```

## Option C: Connect GitHub for Auto-Deploy

To enable automatic deployments on every push:

### 1. Service Settings → Source
- Click on your service
- Go to **"Settings"** tab
- Find **"Source"** section

### 2. Connect Repository
- Click **"Connect to GitHub"**
- Authorize Railway to access your GitHub
- Select repository: `dbbuilder/AI-code-review`
- Select branch: `master`

### 3. Enable Auto-Deploy
- Toggle **"Enable Auto Deploy"** to ON
- Click **"Save"**

### 4. Test Auto-Deploy
- Make a small change (like add a comment)
- Push to master
- Railway should automatically start a new deployment

## Common Build Issues and Solutions

### Issue: Still seeing "$PORT is not a valid integer"

**Cause**: Railway is using cached configuration

**Solutions**:
1. Delete the service and create new one
2. Clear build cache: Settings → Build → Clear Cache → Redeploy
3. Force rebuild: Settings → Redeploy (with "Force Rebuild" checked)

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause**: Python can't find src module

**Solution**: Verify PYTHONPATH
- Go to Settings → Variables
- Add: `PYTHONPATH=/app`
- Redeploy

### Issue: Build succeeds but app crashes immediately

**Causes**:
- Import error in Python code
- Missing dependency
- Port binding issue

**Solution**: Check startup logs
- Go to Deployments → Click deployment → View Logs
- Look for Python traceback
- Check which module failed to import

### Issue: "Application not found" persists

**Causes**:
- Service is stopped
- Service was deleted
- Wrong URL
- Domain not generated

**Solutions**:
1. Check service status in dashboard (should be "Active")
2. Verify public domain exists in Settings → Networking
3. Try generating a new domain
4. Restart the service

## What Should Happen on Successful Deploy

### Build Logs Should Show:
```
Phase: Setup
✓ Installing Python 3.11
✓ Installing gcc, git, curl

Phase: Install
✓ pip install --upgrade pip
✓ pip install -r requirements.txt
✓ Successfully installed:
  - fastapi==0.110.0
  - uvicorn==0.27.0
  - pydantic==2.7.0
  - gitpython==3.1.0
  - (... more packages)

Phase: Build
✓ Build complete

Phase: Start
✓ Running: python -m src.api.main
```

### Runtime Logs Should Show:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Health Check Should Return:
```bash
$ curl https://your-service.up.railway.app/health
{
  "status": "healthy",
  "timestamp": "2025-10-20T12:34:56.789012",
  "service": "autorev-api"
}
```

### API Docs Should Load:
Open in browser: `https://your-service.up.railway.app/docs`

You should see the FastAPI Swagger UI with:
- GET `/` - Root endpoint
- GET `/health` - Health check
- POST `/api/analysis/start` - Start analysis
- GET `/api/analysis/status/{job_id}` - Check status
- GET `/api/analysis/result/{job_id}` - Get results

## Environment Variables to Set (Optional)

In Railway Settings → Variables:

```
PYTHONPATH=/app
ENVIRONMENT=production

# Optional - for AI features (when integrating real crengine)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_GENAI_API_KEY=your-key-here
```

## Files That Control Railway Deployment

All properly configured now:

### 1. railway.json (Highest Priority)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "python -m src.api.main",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311", "gcc", "git", "curl"]

[phases.install]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "python -m src.api.main"
```

### 3. src/api/main.py (Bottom)
```python
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

All three files now use the same approach: `python -m src.api.main`, which properly handles the PORT environment variable in Python.

## Next Steps

1. ✅ **Go to Railway Dashboard**: https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
2. ✅ **Check if service exists** (authentic-nurturing or other name)
3. ✅ **Redeploy** the service to pick up latest code
4. ✅ **Get the correct public URL** from Networking settings
5. ✅ **Test health endpoint** with the actual URL
6. ✅ **View deployment logs** if it fails

## If All Else Fails

**Nuclear Option**: Delete service and recreate
1. Delete "authentic-nurturing" service
2. Create new service from GitHub repo
3. Let Railway auto-detect and build
4. Generate public domain
5. Test endpoints

This ensures no cached configuration or old settings interfere.

---

**Everything is ready in the code** - it just needs to be deployed on Railway with the updated configuration!
