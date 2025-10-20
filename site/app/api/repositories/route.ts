import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken, getGitHubRepositories } from '@/lib/auth';

/**
 * Repositories API
 * Phase 7.3: Fetches user's GitHub repositories
 */
export async function GET(request: NextRequest) {
  const sessionCookie = request.cookies.get('session');

  if (!sessionCookie) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  const session = verifySessionToken(sessionCookie.value);

  if (!session) {
    return NextResponse.json({ error: 'Invalid or expired session' }, { status: 401 });
  }

  try {
    const repositories = await getGitHubRepositories(session.accessToken);

    return NextResponse.json({
      repositories,
      count: repositories.length,
    });
  } catch (error) {
    console.error('Failed to fetch repositories:', error);

    return NextResponse.json(
      { error: 'Failed to fetch repositories' },
      { status: 500 }
    );
  }
}
