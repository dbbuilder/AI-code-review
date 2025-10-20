import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from '@/lib/auth';

/**
 * Start Analysis API
 * Phase 7.4: Proxies analysis requests to Railway backend
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

    // Call Railway backend API
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://authentic-nurturing-production-9807.up.railway.app';

    const backendResponse = await fetch(`${BACKEND_URL}/api/analysis/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_url: repository,
        branch: branch || 'main',
        preset: preset || 'comprehensive',
      }),
    });

    if (!backendResponse.ok) {
      const error = await backendResponse.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to start analysis' },
        { status: backendResponse.status }
      );
    }

    const result = await backendResponse.json();

    return NextResponse.json({
      analysisId: result.id,
      repository,
      preset: preset || 'comprehensive',
      branch: branch || 'main',
      status: result.status,
      message: result.message,
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
