import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from '@/lib/auth';

/**
 * Get Analysis Results API
 * Proxies analysis result requests to Railway backend
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  // Authentication is now optional - analysis results are publicly accessible by ID
  const sessionCookie = request.cookies.get('session');
  const session = sessionCookie ? verifySessionToken(sessionCookie.value) : null;

  try {
    const { id } = params;

    // Call Railway backend API
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://authentic-nurturing-production-9807.up.railway.app';

    const backendResponse = await fetch(`${BACKEND_URL}/api/analysis/result/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!backendResponse.ok) {
      // If analysis not found or not complete, check status
      const statusResponse = await fetch(`${BACKEND_URL}/api/analysis/status/${id}`);
      if (statusResponse.ok) {
        const status = await statusResponse.json();
        return NextResponse.json({
          id,
          status: status.status,
          progress: status.progress,
          message: status.message,
          error: status.error,
        });
      }

      const error = await backendResponse.json();
      return NextResponse.json(
        { error: error.detail || 'Analysis not found' },
        { status: backendResponse.status }
      );
    }

    const result = await backendResponse.json();

    // Transform backend response to frontend format
    return NextResponse.json({
      id: result.id,
      repository: result.repo_url,
      branch: result.branch,
      status: 'completed',
      startedAt: new Date(Date.now() - 300000).toISOString(), // Mock for now
      completedAt: new Date().toISOString(),
      findings: result.findings.map((finding: any) => ({
        id: `finding_${finding.line}`,
        file: finding.file,
        line: finding.line,
        line_end: finding.line_end,
        severity: finding.severity,
        rule: finding.title,
        message: finding.message,
        reasoning: finding.reasoning,
        recommendation: finding.recommendation,
        category: finding.category,
        confidence: finding.confidence,
        difficulty: 3, // Could be calculated from severity
        value: 3, // Could be calculated from category
        phase: getPhaseFromCategory(finding.category),
      })),
      summary: {
        totalFindings: result.total_findings,
        bySeverity: {
          critical: result.critical_findings,
          high: result.high_findings,
          medium: result.medium_findings,
          low: result.low_findings,
          info: 0, // Not in current backend response
        },
        byPhase: {}, // Could be calculated from findings
        estimatedEffort: result.total_findings * 0.5, // Rough estimate
      },
    });
  } catch (error) {
    console.error('Failed to fetch analysis results:', error);

    return NextResponse.json(
      { error: 'Failed to fetch analysis results' },
      { status: 500 }
    );
  }
}

function getPhaseFromCategory(category: string): number {
  const phaseMap: Record<string, number> = {
    'security': 1,
    'bug': 1,
    'performance': 2,
    'maintainability': 3,
    'style': 4,
    'design': 3,
  };
  return phaseMap[category] || 0;
}
