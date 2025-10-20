# Quick Start: Testing AI Code Review (Low Token Usage)

This guide walks you through testing the AI code review system with minimal API costs.

## Prerequisites

- Python 3.10+
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Git

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /mnt/d/Dev2/code-review-engine

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install package
pip install -e .
```

## Step 2: Set API Key

```bash
# Set OpenAI API key (replace with your actual key)
export OPENAI_API_KEY="sk-proj-..."

# Windows PowerShell:
# $env:OPENAI_API_KEY="sk-proj-..."
```

## Step 3: Run Quick Test (Low Token Usage)

This test uses ~500 tokens (~$0.001 with GPT-4o-mini):

```bash
python test_ai_integration.py
```

**Expected Output**:
```
Testing AI integration with OpenAI GPT-4o-mini...
============================================================
✅ Success! Found 2 issues

1. SQL Injection Vulnerability
   Severity: critical
   Category: security
   Lines: 8-9
   Description: User input is directly concatenated into SQL query...
   Confidence: 95%

2. Inefficient Loop Pattern
   Severity: medium
   Category: performance
   Lines: 2-5
   Description: Using addition in loop instead of sum()...
   Confidence: 85%

============================================================
✅ AI integration test passed!
```

## Step 4: Test via API (Railway)

Once you've verified local testing works, test the deployed API:

```bash
# Start analysis on a small test repo (dbbuilder's SQLExtract is a good example)
curl -X POST https://authentic-nurturing-production-9807.up.railway.app/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/dbbuilder/SQLExtract",
    "branch": "main"
  }'

# Response will include job ID:
# {"id": "abc-123-def", "status": "queued", ...}

# Check status (replace {id} with actual job ID)
curl https://authentic-nurturing-production-9807.up.railway.app/api/analysis/status/abc-123-def

# Get results when completed
curl https://authentic-nurturing-production-9807.up.railway.app/api/analysis/result/abc-123-def
```

## Railway Configuration

### Add Environment Variables

1. Go to Railway dashboard: https://railway.app
2. Select your service
3. Click **Variables** tab
4. Add these variables:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
PORT=8080
PYTHONPATH=/app
```

5. Service will automatically redeploy

### Verify Deployment

Check Railway logs:
- Look for "Application startup complete"
- Verify no errors about missing API keys

## Cost Estimates

Using OpenAI GPT-4o-mini (as of 2025):

| Analysis Type | Files Analyzed | Estimated Tokens | Estimated Cost |
|---------------|----------------|------------------|----------------|
| Quick Test | 1 file | ~500 | $0.001 |
| Small Repo | 10 files | ~5,000 | $0.01 |
| Medium Repo | 20 files | ~10,000 | $0.02 |

**Note**: System is capped at 20 files per analysis to prevent runaway costs.

## Troubleshooting

### "No API key found" Error

**Problem**: Railway returns error about missing API key

**Solution**:
1. Verify OPENAI_API_KEY is set in Railway Variables
2. Check for typos in variable name (must be exact)
3. Redeploy after adding variable
4. Check Railway logs for confirmation

### "Failed to parse JSON response" Error

**Problem**: AI returned non-JSON format

**Solution**: This is rare with GPT-4o-mini but can happen. The system has automatic retry logic (3 attempts) with exponential backoff.

### "Repository clone failed" Error

**Problem**: Cannot access private repository

**Solution**: Add `github_token` to request:
```json
{
  "repo_url": "https://github.com/user/private-repo",
  "branch": "main",
  "github_token": "ghp_your_personal_access_token"
}
```

## Next Steps

Once basic testing works:

1. **Test with your own repository**: Replace repo URL with your project
2. **Review findings**: Check quality and actionability of suggestions
3. **Adjust filtering**: Edit `config/smart_filters.yaml` to customize which files are analyzed
4. **Try different providers**: Add ANTHROPIC_API_KEY or OPENROUTER_API_KEY for comparison
5. **Integrate with frontend**: Wire up autorev.servicevision.io to display results

## Support

- **Documentation**: See AI_CODE_REVIEW_IMPLEMENTATION.md
- **GitHub Issues**: https://github.com/dbbuilder/AI-code-review/issues
- **Example Repos**: https://github.com/dbbuilder/SQLExtract (good test case)
