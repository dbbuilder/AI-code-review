# Railway Manual Deployment Steps

## Current Status

✅ Code pushed to GitHub: `dbbuilder/AI-code-review` (master branch)
✅ All configuration files ready:
- `nixpacks.toml` - Build configuration with fixed $PORT handling
- `Procfile` - Start command
- `requirements.txt` - Dependencies
- `src/api/main.py` - FastAPI application with mock data

❌ Service not yet deployed or not accessible at URL

## Error Encountered

```
curl https://authentic-nurturing-production.up.railway.app/health
{"status":"error","code":404,"message":"Application not found"}
```

This means either:
1. The service hasn't been deployed yet
2. The service exists but isn't running
3. GitHub auto-deploy isn't configured

## Manual Deployment Steps

### Step 1: Go to Railway Dashboard

Open your browser and navigate to:
```
https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
```

### Step 2: Check Service Status

Look for the service named **"authentic-nurturing"**:
- If you see it, check if it's **Active** or **Failed**
- Click on it to see deployment logs

### Step 3A: If Service Exists - Redeploy

1. Click on the **"authentic-nurturing"** service
2. Go to **Deployments** tab
3. Check the latest deployment status
4. If it failed, click **"View Logs"** to see what went wrong
5. Go to **Settings** tab
6. Scroll down and click **"Redeploy"** button

### Step 3B: If Service Doesn't Exist - Create New Service

1. Click **"+ New"** button
2. Select **"GitHub Repo"**
3. Choose repository: `dbbuilder/AI-code-review`
4. Select branch: `master`
5. Railway will detect Python and use nixpacks
6. Wait for build to complete

### Step 4: Verify Build Configuration

In the service settings:
1. Go to **Settings** → **Build**
2. Verify **Builder** is set to **"Nixpacks"**
3. Check **Root Directory** is `/` (empty or root)

### Step 5: Check Environment Variables

In the service settings:
1. Go to **Variables** tab
2. Railway should auto-set `PORT` (usually 8080 or dynamically assigned)
3. If needed, you can add:
   - `PYTHONPATH=/app`
   - `ENVIRONMENT=production`

### Step 6: Get the Public URL

1. In service **Settings** → **Networking**
2. Look for **Public Networking**
3. If no domain exists:
   - Click **"Generate Domain"**
   - Railway will create a URL like `service-name-production.up.railway.app`
4. Copy the generated URL

### Step 7: Test the New URL

Once deployed and active, test:

```bash
# Replace with your actual Railway URL
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

### Step 8: Test API Documentation

Open in browser:
```
https://YOUR-SERVICE-URL.up.railway.app/docs
```

You should see the FastAPI Swagger UI.

## Common Issues and Solutions

### Issue: Build Fails with "uvicorn: command not found"

**Solution**: Already fixed! The new nixpacks.toml uses:
```toml
cmd = "sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1'"
```

### Issue: Build Fails with "Invalid value for '--port': '$PORT'"

**Solution**: Already fixed! Using shell wrapper to properly expand environment variable.

### Issue: "Application not found" after deployment

**Causes**:
1. Service hasn't finished deploying yet (check logs)
2. Service crashed on startup (check logs)
3. Wrong URL (verify in Railway dashboard)

**Solution**: Check the deployment logs in Railway dashboard

### Issue: Service starts but returns 502 Bad Gateway

**Causes**:
1. App crashed after starting
2. Port binding issue
3. Python import error

**Solution**:
1. Check logs in Railway dashboard
2. Verify PYTHONPATH is set correctly
3. Ensure all dependencies are in requirements.txt

## Alternative: Connect GitHub for Auto-Deploy

To enable automatic deployments on every git push:

1. Go to service **Settings** → **Source**
2. Click **"Connect to GitHub"**
3. Select repository: `dbbuilder/AI-code-review`
4. Select branch: `master`
5. Enable **"Auto Deploy"**
6. Click **Save**

Now every push to master will automatically trigger a new deployment.

## What to Do After Successful Deployment

Once you get a successful health check:

1. **Update Vercel environment variable**:
   ```bash
   cd /mnt/d/Dev2/code-review-engine/site
   vercel env add NEXT_PUBLIC_API_URL
   # Enter: https://YOUR-RAILWAY-URL.up.railway.app
   ```

2. **Redeploy frontend** to use new API:
   ```bash
   vercel --prod
   ```

3. **Test full flow**:
   - Visit https://autorev.servicevision.io
   - Sign in with GitHub
   - Select a repository
   - Click "Analyze Now"
   - See mock analysis results

## Current Configuration Files

### nixpacks.toml (Fixed)
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
cmd = "sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1'"
```

### Procfile
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

Both files are now properly configured to handle the PORT environment variable.

## Next Steps

1. ✅ Go to Railway dashboard
2. ✅ Check if "authentic-nurturing" service exists
3. ✅ Deploy or redeploy the service
4. ✅ Get the correct public URL
5. ✅ Test the health endpoint
6. ✅ Update frontend with API URL

---

**Railway Project**: https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b

**GitHub Repository**: https://github.com/dbbuilder/AI-code-review

**Last Commit**: Fixed $PORT environment variable expansion in nixpacks.toml
