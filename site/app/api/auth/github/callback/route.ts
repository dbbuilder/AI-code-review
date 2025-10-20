import { NextRequest, NextResponse } from 'next/server';
import { exchangeCodeForToken, getGitHubUser, createSessionToken } from '@/lib/auth';

/**
 * GitHub OAuth Callback Handler
 * Phase 7.2: Handles the OAuth callback from GitHub
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const error = searchParams.get('error');

  // Handle OAuth errors
  if (error) {
    return NextResponse.redirect(
      new URL(`/?error=${encodeURIComponent(error)}`, request.url)
    );
  }

  // Validate code parameter
  if (!code) {
    return NextResponse.redirect(
      new URL('/?error=missing_code', request.url)
    );
  }

  try {
    // Step 1: Exchange code for access token
    const accessToken = await exchangeCodeForToken(code);

    // Step 2: Fetch user information
    const user = await getGitHubUser(accessToken);

    // Step 3: Create session (expires in 7 days)
    const session = {
      user,
      accessToken,
      expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000,
    };

    // Step 4: Create session token
    const sessionToken = createSessionToken(session);

    // Step 5: Create response with redirect
    const response = NextResponse.redirect(new URL('/dashboard', request.url));

    // Step 6: Set secure HTTP-only cookie
    response.cookies.set('session', sessionToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 7 * 24 * 60 * 60, // 7 days
      path: '/',
    });

    return response;
  } catch (err) {
    console.error('GitHub OAuth error:', err);

    const errorMessage = err instanceof Error ? err.message : 'Authentication failed';

    return NextResponse.redirect(
      new URL(`/?error=${encodeURIComponent(errorMessage)}`, request.url)
    );
  }
}
