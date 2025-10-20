# Railway Manual Deployment - Next Steps

## ✅ Project Created Successfully

Your Railway project is created:
- **Project Name**: AutoRev
- **Project ID**: `2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b`
- **Dashboard**: https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b

## Problem

The CLI couldn't complete the deployment because it needs an interactive terminal for service selection.

## Solution: Deploy via Railway Dashboard

### Option 1: Complete Deployment in Dashboard (Recommended)

1. **Open the project in Railway dashboard**:
   ```
   https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
   ```

2. **Create a new service**:
   - Click "+ New" button
   - Select "GitHub Repo"
   - Connect your GitHub account (if not already)
   - Select repository: `code-review-engine`
   - Click "Deploy Now"

3. **Railway will auto-detect**:
   - ✅ Dockerfile
   - ✅ railway.json
   - ✅ requirements.txt
   - Will start building automatically

4. **Wait for deployment** (~2-3 minutes):
   - Watch build logs in the dashboard
   - Service will be assigned a public URL

5. **Get your service URL**:
   - Click on the service
   - Go to "Settings" tab
   - Find "Networking" section
   - Copy the public URL (e.g., `autorev-production-xxxx.up.railway.app`)

### Option 2: Deploy from Terminal (After Linking)

Since the project exists, you need to link to it first:

1. **Open a regular terminal** (not through an automation tool):
   ```bash
   cd /mnt/d/Dev2/code-review-engine
   railway link
   ```

2. **Select from interactive menu**:
   - Workspace: `dbbuilder's Projects`
   - Project: `AutoRev`
   - Environment: `production`

3. **Deploy**:
   ```bash
   railway up
   ```

4. **Get URL**:
   ```bash
   railway domain
   ```

### Option 3: GitHub Integration (Best for Long-Term)

1. **Push to GitHub** (if not already):
   ```bash
   cd /mnt/d/Dev2/code-review-engine
   git add Dockerfile railway.json requirements.txt src/api/
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Connect GitHub in Railway Dashboard**:
   - Open project: https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
   - Click "+ New" → "GitHub Repo"
   - Select your repository
   - Select branch: `main`
   - Railway will auto-deploy

3. **Auto-deploy enabled**:
   - Every push to `main` triggers automatic deployment
   - No need to run `railway up` manually

## After Deployment

Once your service is deployed:

### 1. Test the API

```bash
# Replace YOUR-URL with actual Railway URL
curl https://YOUR-URL.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-20T...",
#   "service": "autorev-api"
# }
```

### 2. View API Documentation

Open in browser:
```
https://YOUR-URL.up.railway.app/docs
```

This shows interactive Swagger UI with all endpoints.

### 3. Set Environment Variables (Optional)

In Railway Dashboard:
- Go to your service
- Click "Variables" tab
- Add these (optional for AI features):
  - `OPENAI_API_KEY` = `sk-...`
  - `ANTHROPIC_API_KEY` = `sk-ant-...`
  - `GOOGLE_GENAI_API_KEY` = `...`

### 4. Connect Frontend to Backend

Update Vercel environment variable:

1. Go to Vercel dashboard
2. Project: `autorev`
3. Settings → Environment Variables
4. Add variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://YOUR-RAILWAY-URL.up.railway.app`
5. Redeploy frontend

## Troubleshooting Build Issues

If the build fails in Railway dashboard:

### Issue 1: Missing Dependencies

**Symptoms**: Build fails with "ModuleNotFoundError"

**Solution**: Ensure all imports in `src/api/main.py` are correct:
```python
# Check this line works:
from src.crengine.main import run_full_pass
```

If crengine isn't set up yet, comment out that import temporarily:
```python
# from src.crengine.main import run_full_pass  # TODO: Uncomment when crengine is ready
```

### Issue 2: Port Binding

**Symptoms**: Service starts but shows "unhealthy"

**Solution**: Railway sets `PORT` environment variable. Update Dockerfile if needed:
```dockerfile
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Change to:
```dockerfile
CMD sh -c "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"
```

### Issue 3: Tree-Sitter or Semgrep Not Found

**Symptoms**: Build succeeds but runtime errors

**Solution**: Add to Dockerfile (already included):
```dockerfile
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## Quick Reference

### Railway Dashboard URLs

- **Project**: https://railway.com/project/2c73a0f5-83a6-4cf0-8dfb-629bbb9a468b
- **Build Logs**: Click on service → Deployments → Latest deployment
- **Environment Variables**: Click on service → Variables
- **Networking**: Click on service → Settings → Networking

### CLI Commands (After Linking)

```bash
# Link to project (run in interactive terminal)
railway link

# Deploy
railway up

# Get service URL
railway domain

# View logs
railway logs

# Open dashboard
railway open

# Check status
railway status
```

## Next Steps

1. **✅ Complete deployment** using Option 1, 2, or 3 above
2. **✅ Test `/health` endpoint** to verify it works
3. **✅ View `/docs` endpoint** to see API documentation
4. **✅ Add environment variables** if using AI features
5. **✅ Connect frontend** by updating Vercel env var

## Expected Costs

- **Starter Plan**: $5/month
- **Compute**: ~$15-20/month
- **Total**: $20-25/month for MVP

Monitor usage in Railway dashboard → Billing section.

---

**Recommendation**: Use **Option 3 (GitHub Integration)** for the best long-term workflow. It enables automatic deployments on every push.
