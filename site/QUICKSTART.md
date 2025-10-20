# AutoVibe Quick Start Guide

## 🚀 Production Deployment

**Live URL**: https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app

**Status**: ✅ Deployed (Building)

---

## 📋 Quick Setup (5 Minutes)

### 1. Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: AutoVibe
   - **Homepage URL**: https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app
   - **Callback URL**: https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app/api/auth/github/callback
4. Click "Register application"
5. Copy Client ID and Client Secret

### 2. Add Environment Variables to Vercel

1. Go to https://vercel.com/dbbuilder-projects-d50f6fce/site
2. Click "Settings" → "Environment Variables"
3. Add these variables:
   ```
   GITHUB_CLIENT_ID = [paste your Client ID]
   GITHUB_CLIENT_SECRET = [paste your Client Secret]
   GITHUB_CALLBACK_URL = https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app/api/auth/github/callback
   NODE_ENV = production
   ```
4. Click "Save"

### 3. Redeploy

1. Go to "Deployments" tab
2. Click "..." menu on latest deployment
3. Click "Redeploy"
4. Wait 2-3 minutes

### 4. Test

1. Visit https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app
2. Click "Sign in with GitHub"
3. Authorize the app
4. You should see your repositories!

---

## 💻 Local Development

### Install Dependencies

```bash
cd site
npm install
```

### Setup Environment

Create `site/.env`:

```bash
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
GITHUB_CALLBACK_URL=http://localhost:3000/api/auth/github/callback
NODE_ENV=development
```

For local development, create a separate GitHub OAuth App with callback URL: `http://localhost:3000/api/auth/github/callback`

### Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

---

## 📁 Project Structure

```
site/
├── app/
│   ├── page.tsx              # Landing page
│   ├── dashboard/            # Repository browser
│   ├── analyze/              # Analysis configuration
│   ├── results/[id]/         # Results display
│   └── api/                  # API routes
├── components/               # React components
├── lib/
│   └── auth.ts              # Authentication utilities
└── ...config files
```

---

## 🔑 Key Features

✅ Landing page with AutoVibe branding
✅ GitHub OAuth authentication
✅ Repository browser with search
✅ Analysis configuration UI
✅ Results visualization dashboard
✅ Responsive design + dark mode
✅ Deployed to Vercel

---

## 🎯 User Flow

1. **Landing** → Click "Sign in with GitHub"
2. **OAuth** → Authorize AutoVibe
3. **Dashboard** → Browse your repositories
4. **Analyze** → Select repo, configure, start
5. **Results** → View findings, filter, export

---

## 📚 Documentation

- **README.md**: Comprehensive guide
- **DEPLOYMENT.md**: Deployment instructions
- **PHASE7_COMPLETE.md**: Complete feature overview
- **QUICKSTART.md**: This file

---

## ⚡ Quick Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Deploy to Vercel
vercel --prod
```

---

## 🐛 Troubleshooting

### "Not authenticated" error
- Check GitHub OAuth app credentials in Vercel
- Verify callback URL matches exactly
- Redeploy after adding environment variables

### Repositories not loading
- Check browser console for errors
- Verify GitHub token has repo scope
- Try signing out and back in

### Build failures
- Check Vercel build logs
- Verify all dependencies are in package.json
- Ensure TypeScript types are correct

---

## 🔗 Important Links

- **Production**: https://site-4se53d7tw-dbbuilder-projects-d50f6fce.vercel.app
- **Vercel Dashboard**: https://vercel.com/dbbuilder-projects-d50f6fce/site
- **GitHub OAuth Apps**: https://github.com/settings/developers
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs

---

## 🎨 Branding

- **Name**: AutoVibe
- **Tagline**: AI Driven Automated Code Review for Vibe Coding Quality
- **Colors**: Indigo (#6366f1) + Purple (#8b5cf6)

---

## 🚧 What's Next (TODO)

- [ ] Verify live deployment works
- [ ] Setup GitHub OAuth credentials
- [ ] Test authentication flow
- [ ] Rename project to "autovibe"
- [ ] Register custom domain
- [ ] Implement FastAPI backend
- [ ] Connect crengine worker
- [ ] Enable real analysis

---

**Questions?** Check the full documentation in PHASE7_COMPLETE.md

**Status**: ✅ Phase 7 Complete | 🚀 Deployed to Production
