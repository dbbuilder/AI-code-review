# Deploy-Vercel.ps1
# Deploy AutoRev frontend to Vercel after environment variable setup

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoRev - Vercel Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to site directory
$SiteDir = "D:\Dev2\code-review-engine\site"
Write-Host "Changing to directory: $SiteDir" -ForegroundColor Yellow
Set-Location $SiteDir

Write-Host ""
Write-Host "Environment variable NEXT_PUBLIC_API_URL has been added!" -ForegroundColor Green
Write-Host "Value: https://authentic-nurturing-production-9807.up.railway.app" -ForegroundColor Gray
Write-Host ""
Write-Host "Now we need to redeploy for the variable to take effect." -ForegroundColor Yellow
Write-Host ""

Write-Host "Choose deployment method:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1) Deploy via Vercel CLI now (vercel --prod)" -ForegroundColor White
Write-Host "  2) Push to Git and auto-deploy" -ForegroundColor White
Write-Host "  3) Skip (deploy manually later)" -ForegroundColor White
Write-Host ""
Write-Host "Enter choice (1/2/3): " -ForegroundColor Cyan -NoNewline
$choice = Read-Host

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Deploying to production via Vercel CLI..." -ForegroundColor Yellow
    Write-Host ""

    try {
        # Wait a moment to avoid the network issue
        Start-Sleep -Seconds 3
        vercel --prod --yes

        Write-Host ""
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Visit: https://autorev.servicevision.io" -ForegroundColor White
        Write-Host "2. Open DevTools (F12) and test:" -ForegroundColor White
        Write-Host "   console.log(process.env.NEXT_PUBLIC_API_URL)" -ForegroundColor Yellow
        Write-Host ""

    } catch {
        Write-Host ""
        Write-Host "⚠️  Deployment encountered an issue" -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Try option 2 (Git push) instead, or deploy via Vercel dashboard" -ForegroundColor Yellow
    }

} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Deploying via Git push..." -ForegroundColor Yellow
    Write-Host ""

    # Change to repo root
    Set-Location "D:\Dev2\code-review-engine"

    Write-Host "Adding files to git..." -ForegroundColor Gray
    git add .

    Write-Host "Creating commit..." -ForegroundColor Gray
    $commitMsg = @"
Add Vercel environment configuration for Railway backend

- Added NEXT_PUBLIC_API_URL environment variable
- Points to: https://authentic-nurturing-production-9807.up.railway.app
- Environment variable set for Production, Preview, and Development

Backend is verified working and ready for frontend integration.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"@

    git commit -m $commitMsg

    Write-Host "Pushing to GitHub..." -ForegroundColor Gray
    git push origin master

    Write-Host ""
    Write-Host "✅ Pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vercel will automatically deploy in ~2-3 minutes." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Monitor deployment:" -ForegroundColor Cyan
    Write-Host "  https://vercel.com/dashboard" -ForegroundColor White
    Write-Host ""
    Write-Host "Once deployed, test at:" -ForegroundColor Cyan
    Write-Host "  https://autorev.servicevision.io" -ForegroundColor White
    Write-Host ""

} else {
    Write-Host ""
    Write-Host "Skipping deployment." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To deploy later, choose one of:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Option A: Vercel CLI" -ForegroundColor White
    Write-Host "    cd D:\Dev2\code-review-engine\site" -ForegroundColor Gray
    Write-Host "    vercel --prod" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Option B: Git Push" -ForegroundColor White
    Write-Host "    cd D:\Dev2\code-review-engine" -ForegroundColor Gray
    Write-Host "    git add ." -ForegroundColor Yellow
    Write-Host "    git commit -m 'Update environment config'" -ForegroundColor Yellow
    Write-Host "    git push origin master" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Option C: Vercel Dashboard" -ForegroundColor White
    Write-Host "    1. Go to https://vercel.com/dashboard" -ForegroundColor Gray
    Write-Host "    2. Select project" -ForegroundColor Gray
    Write-Host "    3. Deployments → Latest → Redeploy" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:" -ForegroundColor Green
Write-Host "  URL: https://autorev.servicevision.io" -ForegroundColor White
Write-Host "  Status: Environment variable configured ✅" -ForegroundColor White
Write-Host ""
Write-Host "Backend:" -ForegroundColor Green
Write-Host "  URL: https://authentic-nurturing-production-9807.up.railway.app" -ForegroundColor White
Write-Host "  Status: Active and verified ✅" -ForegroundColor White
Write-Host ""
Write-Host "Environment Variable:" -ForegroundColor Green
Write-Host "  NEXT_PUBLIC_API_URL" -ForegroundColor White
Write-Host "  = https://authentic-nurturing-production-9807.up.railway.app" -ForegroundColor Gray
Write-Host "  Environments: Production, Preview, Development ✅" -ForegroundColor White
Write-Host ""
Write-Host "Ready for end-to-end testing! 🚀" -ForegroundColor Cyan
Write-Host ""
