import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const hasSession = request.cookies.has("al_access_token");
  if (!hasSession) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.searchParams.set("login", "watchlist");
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/watchlist"],
};
