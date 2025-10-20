# Add-GitHubOAuth-Env.ps1
# Add GitHub OAuth environment variables to Vercel

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub OAuth Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to site directory
$SiteDir = "D:\Dev2\code-review-engine\site"
Write-Host "Changing to directory: $SiteDir" -ForegroundColor Yellow
Set-Location $SiteDir

Write-Host ""
Write-Host "You need to add 3 GitHub OAuth environment variables to Vercel." -ForegroundColor Yellow
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
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Before You Continue" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need to create a GitHub OAuth App first:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://github.com/settings/developers" -ForegroundColor White
Write-Host "2. Click 'OAuth Apps'" -ForegroundColor White
Write-Host "3. Click 'New OAuth App'" -ForegroundColor White
Write-Host "4. Fill in:" -ForegroundColor White
Write-Host "   - Application name: AutoRev" -ForegroundColor Gray
Write-Host "   - Homepage URL: https://autorev.servicevision.io" -ForegroundColor Gray
Write-Host "   - Authorization callback URL: https://autorev.servicevision.io/api/auth/github/callback" -ForegroundColor Gray
Write-Host "5. Click 'Register application'" -ForegroundColor White
Write-Host "6. Copy the Client ID" -ForegroundColor White
Write-Host "7. Click 'Generate a new client secret' and copy it" -ForegroundColor White
Write-Host ""
Write-Host "Do you have your GitHub OAuth Client ID and Client Secret? (Y/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -ne 'Y' -and $response -ne 'y') {
    Write-Host ""
    Write-Host "Please create the OAuth App first, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Quick link: https://github.com/settings/developers" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Add Environment Variables" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variable 1: GITHUB_CLIENT_ID
Write-Host "1/3: Adding GITHUB_CLIENT_ID" -ForegroundColor Yellow
Write-Host ""
Write-Host "Paste your GitHub OAuth Client ID:" -ForegroundColor Cyan -NoNewline
$clientId = Read-Host

if ([string]::IsNullOrWhiteSpace($clientId)) {
    Write-Host ""
    Write-Host "ERROR: Client ID cannot be empty!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running: vercel env add GITHUB_CLIENT_ID" -ForegroundColor Gray
Write-Host ""

try {
    # Create temp file with value
    $clientId | Out-File -FilePath "temp_client_id.txt" -Encoding ASCII -NoNewline

    # Add to Vercel (this will still prompt for environments)
    $env:VERCEL_VALUE = $clientId
    Write-Host "When prompted, select ALL environments (Production, Preview, Development)" -ForegroundColor Magenta
    Write-Host ""
    Start-Sleep -Seconds 2

    vercel env add GITHUB_CLIENT_ID

    Remove-Item "temp_client_id.txt" -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "✅ GITHUB_CLIENT_ID added successfully!" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "❌ Failed to add GITHUB_CLIENT_ID" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Variable 2: GITHUB_CLIENT_SECRET
Write-Host ""
Write-Host "2/3: Adding GITHUB_CLIENT_SECRET" -ForegroundColor Yellow
Write-Host ""
Write-Host "Paste your GitHub OAuth Client Secret:" -ForegroundColor Cyan -NoNewline
$clientSecret = Read-Host

if ([string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host ""
    Write-Host "ERROR: Client Secret cannot be empty!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running: vercel env add GITHUB_CLIENT_SECRET" -ForegroundColor Gray
Write-Host ""

try {
    Write-Host "When prompted, select ALL environments (Production, Preview, Development)" -ForegroundColor Magenta
    Write-Host ""
    Start-Sleep -Seconds 2

    vercel env add GITHUB_CLIENT_SECRET

    Write-Host ""
    Write-Host "✅ GITHUB_CLIENT_SECRET added successfully!" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "❌ Failed to add GITHUB_CLIENT_SECRET" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Variable 3: GITHUB_CALLBACK_URL
Write-Host ""
Write-Host "3/3: Adding GITHUB_CALLBACK_URL" -ForegroundColor Yellow
Write-Host ""
$callbackUrl = "https://autorev.servicevision.io/api/auth/github/callback"
Write-Host "Using callback URL: $callbackUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Running: vercel env add GITHUB_CALLBACK_URL" -ForegroundColor Gray
Write-Host ""

try {
    Write-Host "When prompted for value, paste:" -ForegroundColor Magenta
    Write-Host "  $callbackUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then select ALL environments (Production, Preview, Development)" -ForegroundColor Magenta
    Write-Host ""
    Start-Sleep -Seconds 2

    vercel env add GITHUB_CALLBACK_URL

    Write-Host ""
    Write-Host "✅ GITHUB_CALLBACK_URL added successfully!" -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Host "❌ Failed to add GITHUB_CALLBACK_URL" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Environment Variables Added!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary of variables added:" -ForegroundColor Green
Write-Host "  ✅ GITHUB_CLIENT_ID" -ForegroundColor White
Write-Host "  ✅ GITHUB_CLIENT_SECRET" -ForegroundColor White
Write-Host "  ✅ GITHUB_CALLBACK_URL" -ForegroundColor White
Write-Host ""

# Verify
Write-Host "Verifying environment variables..." -ForegroundColor Yellow
Write-Host ""

try {
    Start-Sleep -Seconds 2
    vercel env ls
} catch {
    Write-Host "Warning: Could not list environment variables" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Redeploy Required" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Environment variables have been added, but you need to redeploy" -ForegroundColor Yellow
Write-Host "for them to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "Would you like to deploy now? (Y/N): " -ForegroundColor Cyan -NoNewline
$deployResponse = Read-Host

if ($deployResponse -eq 'Y' -or $deployResponse -eq 'y') {
    Write-Host ""
    Write-Host "Deploying to production..." -ForegroundColor Yellow
    Write-Host ""

    try {
        Start-Sleep -Seconds 3
        vercel --prod --yes

        Write-Host ""
        Write-Host "✅ Deployment successful!" -ForegroundColor Green

    } catch {
        Write-Host ""
        Write-Host "⚠️  Deployment encountered an issue" -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Deploy manually with: vercel --prod" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Skipping deployment. Deploy later with:" -ForegroundColor Yellow
    Write-Host "  vercel --prod" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or push to Git:" -ForegroundColor Yellow
    Write-Host "  git add ." -ForegroundColor Cyan
    Write-Host "  git commit -m 'Add GitHub OAuth configuration'" -ForegroundColor Cyan
    Write-Host "  git push origin master" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After deployment completes:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Visit: https://autorev.servicevision.io" -ForegroundColor White
Write-Host "2. Click 'Sign in with GitHub'" -ForegroundColor White
Write-Host "3. Authorize the application" -ForegroundColor White
Write-Host "4. You should be redirected to the Dashboard" -ForegroundColor White
Write-Host ""
Write-Host "All environment variables:" -ForegroundColor Cyan
Write-Host "  ✅ NEXT_PUBLIC_API_URL (already set)" -ForegroundColor White
Write-Host "  ✅ GITHUB_CLIENT_ID (just added)" -ForegroundColor White
Write-Host "  ✅ GITHUB_CLIENT_SECRET (just added)" -ForegroundColor White
Write-Host "  ✅ GITHUB_CALLBACK_URL (just added)" -ForegroundColor White
Write-Host ""
Write-Host "Ready for full testing! 🚀" -ForegroundColor Cyan
Write-Host ""
