import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from '@/lib/auth';

/**
 * Start Analysis API
 * Phase 7.3: Triggers code review analysis for a repository
 *
 * TODO Phase 7.4-7.5: Implement actual backend integration with FastAPI worker
 */
export async function POST(request: NextRequest) {
  const sessionCookie = request.cookies.get('session');

  if (!sessionCookie) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  const session = verifySessionToken(sessionCookie.value);

  if (!session) {
    return NextResponse.json({ error: 'Invalid or expired session' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { repository, preset, branch } = body;

    if (!repository) {
      return NextResponse.json({ error: 'Repository is required' }, { status: 400 });
    }

    // Generate analysis ID
    const analysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // TODO Phase 7.4: Store analysis request in database
    // TODO Phase 7.5: Queue job in Celery/Redis worker
    // For now, return mock response

    return NextResponse.json({
      analysisId,
      repository,
      preset: preset || 'comprehensive',
      branch: branch || 'main',
      status: 'queued',
      message: 'Analysis has been queued successfully',
      estimatedTime: 180, // seconds
    });
  } catch (error) {
    console.error('Failed to start analysis:', error);

    return NextResponse.json(
      { error: 'Failed to start analysis' },
      { status: 500 }
    );
  }
}
