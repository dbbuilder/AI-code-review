"""
AutoRev API - FastAPI Backend
Production-ready API for code review analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import crengine modules
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.crengine.smart_filter import filter_repository_files, get_file_summary
from src.crengine.ai_reviewer import review_repository, save_findings_json, generate_markdown_report

app = FastAPI(
    title="AutoRev Code Review API",
    description="AI-driven automated code review engine",
    version="1.0.0"
)

# CORS configuration for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autorev.servicevision.io",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (replace with PostgreSQL in production)
analysis_jobs = {}


class AnalysisRequest(BaseModel):
    """Request to analyze a repository"""
    repo_url: str
    branch: str = "main"
    github_token: Optional[str] = None
    preset: str = "comprehensive"  # security, performance, comprehensive
    ai_provider: Optional[str] = None  # openai, anthropic, gemini, none


class AnalysisStatus(BaseModel):
    """Status of an analysis job"""
    id: str
    status: str  # queued, running, completed, failed
    repo_url: str
    branch: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0  # 0-100
    message: Optional[str] = None
    result_url: Optional[str] = None
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    """Result of code analysis"""
    id: str
    repo_url: str
    branch: str
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    findings: List[dict]
    phased_plan: Optional[str] = None
    recommendations: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AutoRev Code Review API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "autorev-api"
    }


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (remove in production)"""
    return {
        "has_openai_key": bool(os.environ.get("OPENAI_API_KEY")),
        "has_anthropic_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "has_openrouter_key": bool(os.environ.get("OPENROUTER_API_KEY")),
        "openai_key_prefix": os.environ.get("OPENAI_API_KEY", "")[:10] + "..." if os.environ.get("OPENAI_API_KEY") else "NOT_SET",
        "env_keys": [k for k in os.environ.keys() if "API" in k or "KEY" in k]
    }


@app.post("/api/analysis/start", response_model=AnalysisStatus)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new code review analysis

    This endpoint:
    1. Validates the repository URL
    2. Creates an analysis job
    3. Queues the analysis in background
    4. Returns job ID for status polling
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Create job record
    job = {
        "id": job_id,
        "status": "queued",
        "repo_url": request.repo_url,
        "branch": request.branch,
        "preset": request.preset,
        "ai_provider": request.ai_provider,
        "github_token": request.github_token,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "message": "Analysis queued",
        "result_url": None,
        "error": None
    }

    analysis_jobs[job_id] = job

    # Queue background analysis
    background_tasks.add_task(run_analysis, job_id)

    return AnalysisStatus(**job)


@app.get("/api/analysis/status/{job_id}", response_model=AnalysisStatus)
async def get_analysis_status(job_id: str):
    """
    Get status of an analysis job

    Frontend polls this endpoint to check progress
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    job = analysis_jobs[job_id]
    return AnalysisStatus(**job)


@app.get("/api/analysis/result/{job_id}")
async def get_analysis_result(job_id: str):
    """
    Get full results of completed analysis

    Returns detailed findings, recommendations, and phased plan
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    job = analysis_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed yet. Current status: {job['status']}"
        )

    # Load results from outputs directory
    try:
        output_dir = f"/app/outputs/{job_id}"

        # Read findings
        import json
        with open(f"{output_dir}/030_scores.json", "r") as f:
            scores = json.load(f)

        # Read recommendations
        with open(f"{output_dir}/040_recommendations.md", "r") as f:
            recommendations = f.read()

        # Read phased plan
        with open(f"{output_dir}/050_phased_plan.md", "r") as f:
            phased_plan = f.read()

        # Calculate statistics
        findings = scores.get("scored_findings", [])
        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        medium = len([f for f in findings if f.get("severity") == "medium"])
        low = len([f for f in findings if f.get("severity") == "low"])

        return AnalysisResult(
            id=job_id,
            repo_url=job["repo_url"],
            branch=job["branch"],
            total_findings=len(findings),
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
            findings=findings[:100],  # Limit to first 100 for API response
            recommendations=recommendations,
            phased_plan=phased_plan
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load analysis results: {str(e)}"
        )


async def run_analysis(job_id: str):
    """
    Background task to run code analysis

    This function:
    1. Updates job status to "running"
    2. Clones the repository
    3. Runs crengine analysis
    4. Saves results
    5. Updates job status to "completed" or "failed"
    """
    job = analysis_jobs[job_id]

    try:
        # Update status to running
        job["status"] = "running"
        job["started_at"] = datetime.utcnow().isoformat()
        job["message"] = "Cloning repository..."
        job["progress"] = 10

        # Create output directory for this job
        output_dir = f"/app/outputs/{job_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Clone repository to temp directory
        repo_dir = f"/app/temp/{job_id}"
        os.makedirs(repo_dir, exist_ok=True)

        # Clone repo using git
        import subprocess
        clone_cmd = ["git", "clone", "--depth", "1", "--branch", job["branch"]]
        if job.get("github_token"):
            # Insert token into URL for private repos
            repo_url = job["repo_url"]
            if "github.com" in repo_url:
                repo_url = repo_url.replace("https://", f"https://{job['github_token']}@")
            clone_cmd.extend([repo_url, repo_dir])
        else:
            clone_cmd.extend([job["repo_url"], repo_dir])

        job["message"] = "Cloning repository..."
        result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise Exception(f"Failed to clone repository: {result.stderr}")

        # Run analysis
        job["message"] = "Filtering relevant code files..."
        job["progress"] = 30

        import json

        # Step 1: Filter files intelligently
        config_path = Path("/app/config/smart_filters.yaml")
        repo_path = Path(repo_dir)

        filtered_files = filter_repository_files(repo_path, config_path)
        file_summary = get_file_summary(filtered_files, repo_path)

        job["message"] = f"Analyzing {len(filtered_files)} code files with AI..."
        job["progress"] = 40

        # Step 2: Run AI-powered code review
        # Check if AI provider is specified and API key exists
        ai_provider = job.get("ai_provider") or "openai"  # Default to OpenAI
        api_key = None

        if ai_provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        elif ai_provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif ai_provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if api_key:
            # Real AI-powered review
            findings = review_repository(
                files=filtered_files,
                repo_root=repo_path,
                ai_provider=ai_provider,
                api_key=api_key,
                max_files=20  # Limit for cost control
            )

            job["progress"] = 80

            # Save results
            os.makedirs(output_dir, exist_ok=True)

            # Convert findings to format expected by frontend
            scored_findings = []
            for finding in findings:
                scored_findings.append({
                    "file": finding.file,
                    "line": finding.line_start,
                    "line_end": finding.line_end,
                    "severity": finding.severity,
                    "category": finding.category,
                    "title": finding.title,
                    "message": finding.description,
                    "reasoning": finding.reasoning,
                    "recommendation": finding.suggestion,
                    "confidence": finding.confidence
                })

            # Save JSON
            with open(f"{output_dir}/030_scores.json", "w") as f:
                json.dump({
                    "scored_findings": scored_findings,
                    "file_summary": file_summary,
                    "ai_provider": ai_provider
                }, f, indent=2)

            # Generate markdown report
            with open(f"{output_dir}/040_recommendations.md", "w") as f:
                f.write("# AI-Powered Code Review Report\n\n")
                f.write(f"**Analyzed Files**: {len(filtered_files)}\n")
                f.write(f"**AI Provider**: {ai_provider}\n")
                f.write(f"**Total Findings**: {len(findings)}\n\n")

                # Group by severity
                by_severity = {'critical': [], 'high': [], 'medium': [], 'low': [], 'info': []}
                for finding in findings:
                    by_severity[finding.severity].append(finding)

                f.write("## Summary\n\n")
                for severity in ['critical', 'high', 'medium', 'low', 'info']:
                    count = len(by_severity[severity])
                    if count > 0:
                        f.write(f"- **{severity.capitalize()}**: {count}\n")

                f.write("\n---\n\n")

                # Write findings
                for severity in ['critical', 'high', 'medium', 'low', 'info']:
                    issues = by_severity[severity]
                    if not issues:
                        continue

                    f.write(f"## {severity.capitalize()} Issues\n\n")

                    for finding in issues:
                        f.write(f"### {finding.title}\n\n")
                        f.write(f"**File**: `{finding.file}:{finding.line_start}-{finding.line_end}`\n\n")
                        f.write(f"**Category**: {finding.category}\n\n")
                        f.write(f"**Issue**: {finding.description}\n\n")
                        f.write(f"**Why It Matters**: {finding.reasoning}\n\n")
                        f.write(f"**How to Fix**: {finding.suggestion}\n\n")
                        f.write("---\n\n")

            # Generate phased plan
            with open(f"{output_dir}/050_phased_plan.md", "w") as f:
                f.write("# Phased Improvement Plan\n\n")

                # Group by severity for phasing
                if by_severity['critical'] or by_severity['high']:
                    f.write("## Phase 1: Critical & High Priority\n\n")
                    for finding in by_severity['critical'] + by_severity['high']:
                        f.write(f"- **{finding.file}**: {finding.title}\n")
                    f.write("\n")

                if by_severity['medium']:
                    f.write("## Phase 2: Medium Priority\n\n")
                    for finding in by_severity['medium']:
                        f.write(f"- **{finding.file}**: {finding.title}\n")
                    f.write("\n")

                if by_severity['low'] or by_severity['info']:
                    f.write("## Phase 3: Low Priority & Improvements\n\n")
                    for finding in by_severity['low'] + by_severity['info']:
                        f.write(f"- **{finding.file}**: {finding.title}\n")
                    f.write("\n")

        else:
            # No API key - return helpful message
            job["status"] = "failed"
            job["error"] = f"No API key found for {ai_provider}. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable."
            return

        # Mark as completed
        job["status"] = "completed"
        job["completed_at"] = datetime.utcnow().isoformat()
        job["progress"] = 100
        job["message"] = "Analysis completed successfully"
        job["result_url"] = f"/api/analysis/result/{job_id}"

        # Cleanup temp directory
        import shutil
        shutil.rmtree(repo_dir, ignore_errors=True)

    except Exception as e:
        # Mark as failed
        job["status"] = "failed"
        job["completed_at"] = datetime.utcnow().isoformat()
        job["error"] = str(e)
        job["message"] = f"Analysis failed: {str(e)}"
        print(f"Analysis failed for job {job_id}: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
