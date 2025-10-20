# Railway Deployment with Nixpacks - Fixed Configuration

## What I Fixed

Updated `nixpacks.toml` to properly install dependencies in the correct order:

```toml
[phases.setup]
nixPkgs = ["python311", "gcc", "git", "curl"]

[phases.install]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"  # ← This installs uvicorn!
]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1"
```

## How to Redeploy (2 Options)

### Option 1: Railway Dashboard (Fastest)

1. **Go to your service**:
   https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b

2. **Click on "focused-motivation" service**

3. **Go to Settings tab**

4. **Scroll down and click "Redeploy"** button
   - Railway will use the new `nixpacks.toml`
   - This time it will install requirements BEFORE starting

5. **Watch build logs**:
   - Click "Deployments" tab
   - Click on the new deployment
   - You should see: `✓ pip install -r requirements.txt`

### Option 2: Push to GitHub & Auto-Deploy

1. **Commit the new configuration**:
   ```bash
   cd /mnt/d/Dev2/code-review-engine
   git add nixpacks.toml Procfile railway.json requirements.txt src/api/
   git commit -m "Fix Railway nixpacks configuration"
   git push origin main
   ```

2. **Connect GitHub in Railway** (if not already):
   - Service Settings → Source
   - Connect to GitHub repository
   - Select branch: `main`
   - Save

3. **Railway auto-deploys** on every push

## What Will Happen During Build

```
1. Setup Phase
   ✓ Install Python 3.11
   ✓ Install gcc, git, curl

2. Install Phase
   ✓ Upgrade pip
   ✓ Install requirements.txt
     - fastapi
     - uvicorn ← This is the key!
     - pydantic
     - gitpython
     - etc.

3. Build Phase
   ✓ Complete

4. Start Phase
   ✓ Run: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ✓ uvicorn command now exists!
```

## Expected Build Time

- **Setup**: 30 seconds
- **Install**: 1-2 minutes (downloading packages)
- **Build**: 5 seconds
- **Start**: 10 seconds

**Total**: ~2-3 minutes

## After Successful Deployment

### 1. Get Your Service URL

In Railway dashboard:
- Click on your service
- Look for the public URL (e.g., `focused-motivation-production-xxxx.up.railway.app`)

Or via CLI:
```bash
railway domain
```

### 2. Test Health Endpoint

```bash
curl https://YOUR-URL.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T12:34:56.789Z",
  "service": "autorev-api"
}
```

### 3. Test API Documentation

Open in browser:
```
https://YOUR-URL.up.railway.app/docs
```

You'll see interactive Swagger UI with all API endpoints.

### 4. Test Root Endpoint

```bash
curl https://YOUR-URL.up.railway.app/
```

Expected response:
```json
{
  "service": "AutoRev Code Review API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs"
}
```

## Troubleshooting

### If Build Still Fails

**Check the exact error** in Railway dashboard:
1. Click service → Deployments
2. Click failed deployment
3. Read build logs

**Common issues**:

#### "Module not found"
- **Cause**: Missing dependency in requirements.txt
- **Fix**: Add the missing package to requirements.txt

#### "Port binding error"
- **Cause**: App not listening on $PORT
- **Fix**: Already handled in nixpacks.toml

#### "Out of memory"
- **Cause**: Too many dependencies or large packages
- **Fix**: Upgrade Railway plan or reduce dependencies

### If App Starts But Returns 502

**Cause**: App crashed after starting

**Check logs**:
```bash
railway logs
```

Or in dashboard: Service → Logs tab

**Common causes**:
- Import error (missing crengine module)
- Port binding issue
- Python version mismatch

## Files That Control Build

1. **`nixpacks.toml`** ✅ (just fixed)
   - Defines build phases
   - Installs dependencies
   - Sets start command

2. **`Procfile`** ✅
   - Backup start command
   - Railway uses nixpacks.toml first

3. **`requirements.txt`** ✅
   - Lists all Python packages
   - Includes uvicorn, fastapi, etc.

4. **`railway.json`** ✅
   - Service configuration
   - Environment settings

## Next Steps After Successful Deployment

1. **✅ Verify all endpoints work**
2. **✅ Add environment variables** (optional for AI):
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_GENAI_API_KEY`

3. **✅ Add custom domain** (optional):
   - Settings → Networking → Add Domain
   - Use: `api.autorev.servicevision.io`

4. **✅ Connect frontend**:
   - Update Vercel env var: `NEXT_PUBLIC_API_URL`
   - Redeploy frontend

5. **✅ Set up monitoring**:
   - Railway provides basic metrics
   - Add Sentry for error tracking (optional)

## Quick Commands Summary

```bash
# Redeploy from CLI (in interactive terminal)
railway up

# Check status
railway status

# View logs
railway logs

# Open in browser
railway open

# Get domain
railway domain
```

---

**Action Required**: Go to Railway dashboard and click **"Redeploy"** button to rebuild with the fixed configuration.

The new `nixpacks.toml` will ensure dependencies are installed before starting the app.
