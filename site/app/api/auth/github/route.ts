import { NextRequest, NextResponse } from 'next/server';
import { getGitHubAuthUrl } from '@/lib/auth';

/**
 * GitHub OAuth Initiation
 * Phase 7.2: Redirects user to GitHub OAuth authorization
 */
export async function GET(request: NextRequest) {
  // Generate random state for CSRF protection
  const state = Math.random().toString(36).substring(7);

  // Store state in cookie for validation in callback
  const response = NextResponse.redirect(getGitHubAuthUrl(state));

  response.cookies.set('oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 600, // 10 minutes
    path: '/',
  });

  return response;
}
