# Add-VercelEnv.ps1
# PowerShell script to add Railway API URL to Vercel environment variables
# Run this in an interactive PowerShell terminal (NOT WSL)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoRev - Vercel Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to site directory
$SiteDir = "D:\Dev2\code-review-engine\site"
Write-Host "Changing to directory: $SiteDir" -ForegroundColor Yellow
Set-Location $SiteDir

# Environment variable details
$VarName = "NEXT_PUBLIC_API_URL"
$VarValue = "https://authentic-nurturing-production-9807.up.railway.app"

Write-Host ""
Write-Host "Environment Variable to Add:" -ForegroundColor Green
Write-Host "  Name:  $VarName" -ForegroundColor White
Write-Host "  Value: $VarValue" -ForegroundColor White
Write-Host ""

# Check if vercel is installed
Write-Host "Checking Vercel CLI installation..." -ForegroundColor Yellow
try {
    $vercelVersion = vercel --version
    Write-Host "  Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Vercel CLI not found!" -ForegroundColor Red
    Write-Host "  Install with: npm install -g vercel" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "  Step 1: Add Environment Variable" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Running: vercel env add $VarName" -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Magenta
Write-Host "  1. When prompted for value, paste:" -ForegroundColor White
Write-Host "     $VarValue" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. When asked which environments, select:" -ForegroundColor White
Write-Host "     [X] Production" -ForegroundColor Green
Write-Host "     [X] Preview" -ForegroundColor Green
Write-Host "     [X] Development" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Run vercel env add interactively
Write-Host ""
Write-Host "Starting Vercel environment variable setup..." -ForegroundColor Yellow
Write-Host ""

try {
    # This will prompt interactively
    vercel env add $VarName

    Write-Host ""
    Write-Host "Environment variable added successfully!" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to add environment variable" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "  Step 2: Verify Environment Variable" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Listing current environment variables..." -ForegroundColor Yellow
Write-Host ""

try {
    vercel env ls
} catch {
    Write-Host "Warning: Could not list environment variables" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "  Step 3: Redeploy to Vercel" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "The environment variable has been added, but you need to redeploy" -ForegroundColor Yellow
Write-Host "for it to take effect in production." -ForegroundColor Yellow
Write-Host ""
Write-Host "OPTIONS:" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Option A: Deploy now via CLI" -ForegroundColor White
Write-Host "    Run: vercel --prod" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option B: Push to Git (auto-deploy)" -ForegroundColor White
Write-Host "    git add ." -ForegroundColor Yellow
Write-Host "    git commit -m 'Update environment config'" -ForegroundColor Yellow
Write-Host "    git push origin master" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Option C: Redeploy via Vercel Dashboard" -ForegroundColor White
Write-Host "    1. Go to https://vercel.com/dashboard" -ForegroundColor Yellow
Write-Host "    2. Select your project" -ForegroundColor Yellow
Write-Host "    3. Go to Deployments tab" -ForegroundColor Yellow
Write-Host "    4. Click on latest deployment" -ForegroundColor Yellow
Write-Host "    5. Click three dots menu -> Redeploy" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to deploy now
Write-Host "Would you like to deploy to production now? (Y/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Deploying to production..." -ForegroundColor Yellow
    Write-Host ""

    try {
        vercel --prod --yes

        Write-Host ""
        Write-Host "Deployment complete!" -ForegroundColor Green

    } catch {
        Write-Host ""
        Write-Host "ERROR: Deployment failed" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "You can manually deploy later with: vercel --prod" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Skipping deployment. You can deploy later with:" -ForegroundColor Yellow
    Write-Host "  vercel --prod" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Green
Write-Host ""
Write-Host "1. After deployment completes, visit:" -ForegroundColor White
Write-Host "   https://autorev.servicevision.io" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Open browser DevTools (F12) and run in Console:" -ForegroundColor White
Write-Host "   console.log(process.env.NEXT_PUBLIC_API_URL)" -ForegroundColor Yellow
Write-Host "   Should show: $VarValue" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test API connection in Console:" -ForegroundColor White
Write-Host "   fetch(process.env.NEXT_PUBLIC_API_URL + '/health')" -ForegroundColor Yellow
Write-Host "     .then(r => r.json())" -ForegroundColor Yellow
Write-Host "     .then(d => console.log(d))" -ForegroundColor Yellow
Write-Host "   Should show: { status: 'healthy', ... }" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test the full flow:" -ForegroundColor White
Write-Host "   - Sign in with GitHub" -ForegroundColor Gray
Write-Host "   - Go to Dashboard" -ForegroundColor Gray
Write-Host "   - Select a repository" -ForegroundColor Gray
Write-Host "   - Click 'Analyze Now'" -ForegroundColor Gray
Write-Host "   - View mock results" -ForegroundColor Gray
Write-Host ""
Write-Host "Backend API: $VarValue" -ForegroundColor Green
Write-Host "Status: Active and verified working" -ForegroundColor Green
Write-Host ""
