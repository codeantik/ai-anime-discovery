// Proxied through next.config.ts rewrites() so the browser only ever talks to
// this site's own origin — keeps the AniList auth cookie first-party instead
// of cross-site between Vercel and Render.
export const BACKEND_URL = "/api/backend";
