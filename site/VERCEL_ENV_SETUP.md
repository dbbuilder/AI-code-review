# Vercel Environment Variable Setup

## Railway API URL Configuration

The AutoRev frontend needs to know where the backend API is hosted. Since the Vercel CLI requires interactive input (TTY) for adding environment variables, you have **two options**:

---

## Option 1: Vercel Dashboard (Recommended - Easiest)

### Step 1: Go to Vercel Project Settings

1. Open browser and go to: https://vercel.com/dashboard
2. Find project: **autorev** (or dbbuilder-projects-d50f6fce/autorev)
3. Click on the project
4. Go to **Settings** tab
5. Click **Environment Variables** in the left sidebar

### Step 2: Add Environment Variable

Click **Add New** button and enter:

**Name:**
```
NEXT_PUBLIC_API_URL
```

**Value:**
```
https://authentic-nurturing-production-9807.up.railway.app
```

**Environments:** Check all boxes:
- ✅ Production
- ✅ Preview
- ✅ Development

Click **Save**.

### Step 3: Redeploy

After saving the environment variable, you need to redeploy:

**Option A: Trigger via Git Push**
```bash
cd /mnt/d/Dev2/code-review-engine/site
git add .
git commit -m "Update environment configuration for Railway backend"
git push origin master
```
Vercel will automatically redeploy.

**Option B: Redeploy via Dashboard**
1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click the **︙** (three dots) menu
4. Select **Redeploy**
5. Confirm redeploy

### Step 4: Verify

After deployment completes:
1. Visit https://autorev.servicevision.io
2. Open browser DevTools (F12)
3. Go to Console
4. Type: `process.env.NEXT_PUBLIC_API_URL`
5. Should show: `https://authentic-nurturing-production-9807.up.railway.app`

---

## Option 2: Interactive Terminal (If You Have Access)

If you can run commands in an interactive PowerShell/CMD (not WSL):

### Step 1: Open PowerShell
```powershell
cd D:\Dev2\code-review-engine\site
```

### Step 2: Add Environment Variable
```powershell
vercel env add NEXT_PUBLIC_API_URL
```

When prompted:
- **What's the value?**: `https://authentic-nurturing-production-9807.up.railway.app`
- **Add to which Environments?**: Select all (Production, Preview, Development)

### Step 3: Redeploy
```powershell
vercel --prod
```

---

## Option 3: Create .env.production File (Quick Test)

For a quick test without Vercel environment variables:

### Step 1: Create .env.production
```bash
cd /mnt/d/Dev2/code-review-engine/site
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL=https://authentic-nurturing-production-9807.up.railway.app
EOF
```

### Step 2: Commit and Push
```bash
git add .env.production
git commit -m "Add production environment configuration"
git push origin master
```

**Note**: This is less secure than Vercel environment variables (values visible in Git), but works for testing.

---

## Verification After Setup

### 1. Check Environment Variable is Set

Visit the deployed site and open DevTools Console:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
// Should output: https://authentic-nurturing-production-9807.up.railway.app
```

### 2. Test API Connection

In DevTools Console:
```javascript
fetch(process.env.NEXT_PUBLIC_API_URL + '/health')
  .then(r => r.json())
  .then(d => console.log(d))
// Should output: { status: "healthy", timestamp: "...", service: "autorev-api" }
```

### 3. Test Full Flow

1. Sign in with GitHub at https://autorev.servicevision.io
2. Go to Dashboard
3. Select a repository
4. Click "Analyze Now"
5. Should see analysis start and complete with mock results

---

## Current Configuration

### Railway Backend API
- **URL**: https://authentic-nurturing-production-9807.up.railway.app
- **Status**: ✅ Active and running
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /` - Service info
  - `GET /docs` - API documentation
  - `POST /api/analysis/start` - Start analysis
  - `GET /api/analysis/status/{id}` - Check progress
  - `GET /api/analysis/result/{id}` - Get results

### Vercel Frontend
- **URL**: https://autorev.servicevision.io
- **Status**: Deployed
- **Needs**: `NEXT_PUBLIC_API_URL` environment variable

---

## Troubleshooting

### Issue: "NEXT_PUBLIC_API_URL is undefined"

**Cause**: Environment variable not set or frontend not redeployed after setting it.

**Solution**:
1. Verify variable is set in Vercel dashboard (Settings → Environment Variables)
2. Redeploy the frontend
3. Hard refresh browser (Ctrl+Shift+R)

### Issue: "Failed to fetch" or CORS errors

**Cause**: Railway backend CORS not configured for frontend domain.

**Solution**: Check that `/src/api/main.py` has:
```python
allow_origins=[
    "https://autorev.servicevision.io",
    "http://localhost:3000",
]
```

✅ Already configured correctly!

### Issue: API returns 404

**Cause**: Railway backend not running or wrong URL.

**Solution**: Test Railway directly:
```bash
curl https://authentic-nurturing-production-9807.up.railway.app/health
```

Should return:
```json
{"status":"healthy","timestamp":"...","service":"autorev-api"}
```

### Issue: Analysis fails or hangs

**Cause**: Backend error (check Railway logs).

**Solution**:
1. Go to Railway dashboard
2. Click service → Deployments → View Logs
3. Look for Python errors
4. Check which step failed

---

## Next Steps After Setup

Once the environment variable is configured and deployed:

1. ✅ Test health endpoint from frontend
2. ✅ Test starting an analysis
3. ✅ Test polling for status
4. ✅ Test displaying results
5. ✅ Test posting to GitHub (if implemented)

---

## Summary

**Recommended Path**:
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL = https://authentic-nurturing-production-9807.up.railway.app`
3. Save and redeploy
4. Test at https://autorev.servicevision.io

This is the cleanest and most secure approach for production deployments.
