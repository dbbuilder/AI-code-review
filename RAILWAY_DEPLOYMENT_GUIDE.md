# Railway Deployment Guide for AutoRev

## ✅ Pre-Deployment Checklist

All required files have been created:
- ✅ `Dockerfile` - Container configuration
- ✅ `railway.json` - Railway service configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `src/api/main.py` - FastAPI application
- ✅ Railway CLI installed (v4.6.3)

---

## Step-by-Step Deployment

### Step 1: Login to Railway

```bash
railway login
```

This will open your browser to authenticate with Railway.

### Step 2: Initialize Railway Project

```bash
cd /mnt/d/Dev2/code-review-engine
railway init
```

Options:
- Choose: "Create a new project"
- Project name: "autorev-api"
- Select your team/account

### Step 3: Link to Existing Project (Alternative)

If you already have a Railway project:

```bash
railway link
```

Then select your project from the list.

### Step 4: Set Environment Variables

```bash
# Optional: OpenAI API Key for AI features
railway variables set OPENAI_API_KEY=your_openai_key_here

# Optional: Anthropic API Key
railway variables set ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Google Gemini API Key
railway variables set GOOGLE_GENAI_API_KEY=your_google_key_here

# Production environment
railway variables set NODE_ENV=production
```

### Step 5: Add PostgreSQL Database (Optional for now)

```bash
railway add --database postgresql
```

This will provision a PostgreSQL database and automatically set `DATABASE_URL` environment variable.

For now, we can skip this as the API uses in-memory storage initially.

### Step 6: Deploy to Railway

```bash
railway up
```

This will:
1. Build the Docker container
2. Push to Railway
3. Deploy the service
4. Assign a public URL

### Step 7: Get Your API URL

```bash
railway domain
```

This shows your public API URL, something like:
`autorev-api-production-xxxx.up.railway.app`

### Step 8: Test the Deployment

```bash
# Test health endpoint
curl https://your-railway-url.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-20T...",
#   "service": "autorev-api"
# }
```

---

## Quick Deploy Commands

If you've already set everything up:

```bash
# Deploy latest changes
railway up

# View logs
railway logs

# Open service in browser
railway open

# Check service status
railway status

# SSH into container (for debugging)
railway shell
```

---

## Environment Variables Reference

### Required
None! The API works without environment variables for basic functionality.

### Optional (AI Features)

```bash
# OpenAI (GPT-4, GPT-3.5)
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GOOGLE_GENAI_API_KEY=...
```

### Database (Future)

```bash
# Automatically set by Railway when you add PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Railway Dashboard Configuration

After deployment, configure in Railway dashboard (https://railway.app):

### 1. Custom Domain (Optional)

- Go to your service settings
- Click "Networking" → "Add Domain"
- Enter: `api.autorev.servicevision.io`
- Add CNAME record in Name.com:
  - Host: `api.autorev`
  - Value: `your-railway-domain.up.railway.app`

### 2. Health Checks

Railway automatically monitors `/health` endpoint.

### 3. Resource Limits

Default limits are fine for MVP:
- 512 MB RAM
- 1 vCPU
- Can upgrade in service settings

### 4. Auto-Deploy from GitHub

1. Go to service settings
2. Click "Source"
3. Connect to GitHub repository
4. Select branch: `main` or `master`
5. Railway will auto-deploy on push

---

## API Endpoints

Once deployed, your API will have these endpoints:

### Health Check
```bash
GET https://your-railway-url/health
```

### Root
```bash
GET https://your-railway-url/
# Returns service info and docs link
```

### API Documentation
```bash
GET https://your-railway-url/docs
# Interactive Swagger UI
```

### Start Analysis
```bash
POST https://your-railway-url/api/analysis/start
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main",
  "github_token": "ghp_...",  // Optional for private repos
  "preset": "comprehensive",
  "ai_provider": "openai"  // Optional: openai, anthropic, gemini, or null
}

# Response:
{
  "id": "uuid",
  "status": "queued",
  "repo_url": "...",
  "branch": "main",
  "created_at": "2025-10-20T...",
  "progress": 0,
  "message": "Analysis queued"
}
```

### Check Status
```bash
GET https://your-railway-url/api/analysis/status/{job_id}

# Response:
{
  "id": "uuid",
  "status": "completed",  // queued, running, completed, failed
  "progress": 100,
  "message": "Analysis completed successfully",
  "result_url": "/api/analysis/result/uuid"
}
```

### Get Results
```bash
GET https://your-railway-url/api/analysis/result/{job_id}

# Response:
{
  "id": "uuid",
  "repo_url": "...",
  "total_findings": 42,
  "critical_findings": 3,
  "high_findings": 8,
  "findings": [...],
  "recommendations": "...",  // Markdown
  "phased_plan": "..."  // Markdown
}
```

---

## Connecting Frontend to Backend

Update your Next.js environment variables:

```bash
# /mnt/d/Dev2/code-review-engine/site/.env.local
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
```

Or add to Vercel environment variables:
1. Go to Vercel dashboard
2. Project settings → Environment Variables
3. Add: `NEXT_PUBLIC_API_URL` = `https://your-railway-url.up.railway.app`
4. Redeploy

---

## Monitoring & Debugging

### View Logs
```bash
# Real-time logs
railway logs

# Or in dashboard:
# https://railway.app → Your Project → Logs
```

### Common Issues

#### Issue 1: Build Fails
```bash
# Check Dockerfile syntax
railway logs --deployment

# Solution: Verify all paths in Dockerfile are correct
```

#### Issue 2: Port Binding Error
```bash
# Railway sets PORT environment variable
# Make sure your app uses $PORT, not hardcoded 8080
```

Fix in main.py:
```python
import os
port = int(os.getenv("PORT", 8080))
uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Issue 3: Out of Memory
```bash
# Upgrade service resources in Railway dashboard
# Settings → Resources → Increase RAM
```

#### Issue 4: Slow Cold Starts
```bash
# Add minimum replicas in railway.json
{
  "deploy": {
    "numReplicas": 1,
    "minScale": 1
  }
}
```

---

## Cost Management

### Current Configuration
- **Starter Plan**: $5/month minimum
- **Compute**: ~$15-20/month for typical usage
- **PostgreSQL**: $5/month (when added)

**Expected Total**: $20-25/month for MVP

### Monitoring Usage
```bash
railway usage

# Or check dashboard:
# https://railway.app → Billing → Usage
```

### Cost Optimization Tips
1. **Don't add database yet** - Use in-memory storage for MVP
2. **Set deployment timeout** - Prevent runaway costs
3. **Monitor logs** - Catch issues early
4. **Use appropriate instance size** - Don't over-provision

---

## GitHub Integration (Auto-Deploy)

Once your repo is on GitHub:

1. **Push code to GitHub**
   ```bash
   cd /mnt/d/Dev2/code-review-engine
   git add Dockerfile railway.json requirements.txt src/api/
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Connect to Railway**
   - Railway dashboard → Your service → Settings
   - Source → Connect to GitHub
   - Select repository and branch
   - Save

3. **Auto-deploy enabled**
   - Every push to `main` triggers deployment
   - See build logs in Railway dashboard
   - Rollback available if needed

---

## Scaling for Production

When you grow beyond MVP:

### Horizontal Scaling
```bash
# Increase replicas in railway.json
{
  "deploy": {
    "numReplicas": 3,
    "minScale": 1,
    "maxScale": 10
  }
}
```

### Add PostgreSQL
```bash
railway add --database postgresql

# Update main.py to use DATABASE_URL instead of in-memory storage
```

### Add Redis (Job Queue)
```bash
railway add --database redis

# Implement Celery for background tasks
```

### Add Monitoring
```bash
# Add Sentry for error tracking
railway variables set SENTRY_DSN=your_sentry_dsn
```

---

## Migration to Google Cloud Run (Future)

When you're ready to migrate (6+ months):

1. Export Railway environment variables
2. Build same Docker image
3. Push to Google Container Registry
4. Deploy to Cloud Run
5. Update frontend API_URL
6. Test thoroughly
7. Switch DNS

Railway → Cloud Run migration is straightforward since both use Docker.

---

## Checklist for Production Readiness

### MVP (Now)
- ✅ Dockerfile created
- ✅ railway.json configured
- ✅ FastAPI app with health endpoint
- ✅ CORS enabled for frontend
- ⏳ Deploy to Railway
- ⏳ Test API endpoints
- ⏳ Connect frontend

### Production (Later)
- ⏳ Add PostgreSQL database
- ⏳ Implement proper job queue (Celery + Redis)
- ⏳ Add authentication middleware
- ⏳ Implement rate limiting
- ⏳ Add Sentry error tracking
- ⏳ Set up monitoring/alerting
- ⏳ Add automated tests
- ⏳ Configure custom domain
- ⏳ Set up CI/CD pipeline
- ⏳ Add backup strategy

---

## Quick Start Summary

```bash
# 1. Login
railway login

# 2. Initialize project
cd /mnt/d/Dev2/code-review-engine
railway init

# 3. Deploy
railway up

# 4. Get URL
railway domain

# 5. Test
curl https://your-url/health

# Done! 🎉
```

---

## Support & Troubleshooting

### Railway Documentation
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Twitter: @Railway

### Common Commands
```bash
railway help           # Show all commands
railway status         # Service status
railway logs           # View logs
railway shell          # SSH into container
railway variables      # List env vars
railway restart        # Restart service
railway down           # Stop service
railway up             # Deploy service
```

---

**Next Step**: Run `railway login` and then `railway init` to get started!
