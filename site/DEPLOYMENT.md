# AutoVibe Deployment Guide

## Current Deployment Status

**Status**: ✅ Deployed to Vercel

**Production URL**: https://site-eu6f1ln1y-dbbuilder-projects-d50f6fce.vercel.app

**Inspection URL**: https://vercel.com/dbbuilder-projects-d50f6fce/site/4tBnbJ8zpxG9K1xngMM5ZRsK3Zvy

**Deployment Date**: 2025-10-20

---

## Deployment Information

### Platform
- **Provider**: Vercel
- **Framework**: Next.js 14 (App Router)
- **Build Command**: `npm run build`
- **Install Command**: `npm install`
- **Output Directory**: `.next`
- **Region**: iad1 (US East)

### Project Details
- **Project Name**: site (will be renamed to autovibe)
- **Team**: dbbuilder-projects-d50f6fce
- **Type**: Production deployment

---

## Vercel Dashboard Access

To manage your deployment:

1. Visit: https://vercel.com/dbbuilder-projects-d50f6fce/site
2. View deployments, logs, analytics
3. Configure custom domain
4. Set environment variables
5. Manage project settings

---

## Renaming the Project to "AutoVibe"

The project is currently named "site". To rename it:

### Via Vercel Dashboard

1. Go to https://vercel.com/dbbuilder-projects-d50f6fce/site
2. Click **Settings** tab
3. Scroll to **Project Name**
4. Change "site" to "autovibe" (lowercase required)
5. Click **Save**

### Note
- Project names must be lowercase
- Use "autovibe" not "AutoVibe"
- After renaming, the URL will become: `https://autovibe.vercel.app`

---

## Custom Domain Setup

To use a custom domain (e.g., autovibe.dev):

### 1. Register Domain
- Register `autovibe.dev` or similar via Vercel Domains, Namecheap, or Name.com

### 2. Add Domain in Vercel
1. Go to Project Settings → Domains
2. Click **Add Domain**
3. Enter your domain (e.g., `autovibe.dev`)
4. Follow DNS configuration instructions

### 3. DNS Configuration
Add these records to your DNS provider:

```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 4. SSL Certificate
- Vercel automatically provisions SSL via Let's Encrypt
- HTTPS will be enabled within minutes

---

## Environment Variables

To add environment variables (for Phase 7.2+):

1. Go to Project Settings → Environment Variables
2. Add variables:
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`
   - `GITHUB_CALLBACK_URL`
   - `NEXT_PUBLIC_API_URL`
   - `API_SECRET_KEY`
3. Set scope (Production, Preview, Development)
4. Redeploy for changes to take effect

---

## Deployment Commands

### Deploy to Production
```bash
cd site
vercel --prod
```

### Deploy to Preview
```bash
cd site
vercel
```

### View Deployments
```bash
vercel ls
```

### View Logs
```bash
vercel logs <deployment-url>
```

### Cancel Deployment
```bash
vercel cancel <deployment-id>
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./site
          vercel-args: '--prod'
```

### Required Secrets
- `VERCEL_TOKEN`: Get from Vercel Account Settings → Tokens
- `VERCEL_ORG_ID`: Found in `.vercel/project.json`
- `VERCEL_PROJECT_ID`: Found in `.vercel/project.json`

---

## Monitoring & Analytics

### Vercel Analytics

Enable in dashboard:
1. Go to Analytics tab
2. Enable Web Analytics (free)
3. View real-time visitor data

### Performance Monitoring

Check in dashboard:
1. Go to Speed Insights tab
2. View Core Web Vitals
3. Identify performance bottlenecks

### Logs

View deployment logs:
1. Go to Deployments tab
2. Click on specific deployment
3. View Build Logs and Function Logs

---

## Troubleshooting

### Build Failures

If build fails:
1. Check Build Logs in Vercel dashboard
2. Verify `package.json` dependencies
3. Ensure `next.config.mjs` is correct
4. Check Node.js version compatibility

### Missing Dependencies

If dependencies fail to install:
```bash
cd site
rm -rf node_modules package-lock.json
npm install
vercel --prod
```

### Environment Variables Not Working

1. Ensure variables are set in Vercel dashboard
2. Variables starting with `NEXT_PUBLIC_` are client-side
3. Other variables are server-side only
4. Redeploy after changing variables

### Domain Not Working

1. Verify DNS records are correct
2. Wait for DNS propagation (up to 48 hours)
3. Check domain status in Vercel dashboard
4. Ensure SSL certificate is active

---

## Performance Optimization

### Image Optimization
- Use Next.js Image component: `import Image from 'next/image'`
- Vercel automatically optimizes images

### Caching
- Static pages are cached by default
- Use ISR (Incremental Static Regeneration) for dynamic pages

### Edge Functions
- Deploy API routes to edge locations for faster response times

---

## Cost Estimation

### Vercel Free Tier
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS
- Analytics

### Vercel Pro ($20/month)
- 1 TB bandwidth/month
- Team collaboration
- Advanced analytics
- Password protection
- Commercial use

---

## Next Steps

1. ✅ **Verify Deployment**: Visit the production URL
2. ⏳ **Rename Project**: Change "site" to "autovibe" in settings
3. ⏳ **Custom Domain**: Register and configure autovibe.dev
4. ⏳ **Enable Analytics**: Turn on Vercel Analytics
5. ⏳ **GitHub OAuth**: Begin Phase 7.2 implementation
6. ⏳ **Environment Variables**: Add when backend is ready

---

## Support

### Vercel Support
- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/next.js/discussions
- Support: support@vercel.com (Pro plan)

### AutoVibe Support
- GitHub Issues: Open issue in repository
- Documentation: See README.md in `/site`

---

**Last Updated**: 2025-10-20
**Deployment Tool**: Vercel CLI 48.2.0
**Framework**: Next.js 14.2.0
