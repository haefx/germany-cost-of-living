import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "gcol_session";
const AUTH_PATHS = ["/login", "/register", "/forgot-password", "/reset-password"];

/** Redirects based on session-cookie *presence* only — a cheap, purely
 * structural check. It does not verify the cookie is still valid (that
 * would mean an extra network call to the API on every navigation); an
 * expired or revoked session still reaches the page, which then gets a 401
 * from the API and redirects client-side. See use-session.ts.
 */
export function proxy(request: NextRequest) {
  const hasSession = request.cookies.has(SESSION_COOKIE);
  const { pathname } = request.nextUrl;
  const isAuthPath = AUTH_PATHS.some((path) => pathname.startsWith(path));

  if (!hasSession && !isAuthPath) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  if (hasSession && isAuthPath) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
