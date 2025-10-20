import { NextRequest, NextResponse } from 'next/server';

/**
 * Sign Out Handler
 * Phase 7.2: Clears session cookie and redirects to home
 */
export async function POST(request: NextRequest) {
  const response = NextResponse.redirect(new URL('/', request.url));

  // Clear session cookie
  response.cookies.set('session', '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 0,
    path: '/',
  });

  return response;
}

export async function GET(request: NextRequest) {
  return POST(request);
}
