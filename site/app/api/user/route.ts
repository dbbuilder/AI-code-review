import { NextRequest, NextResponse } from 'next/server';
import { verifySessionToken } from '@/lib/auth';

/**
 * User Info API
 * Phase 7.2: Returns current user information from session
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

  return NextResponse.json({
    user: session.user,
    expiresAt: session.expiresAt,
  });
}
