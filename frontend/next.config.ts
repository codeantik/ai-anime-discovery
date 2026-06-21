import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8001";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "*.anilist.co" },
      { protocol: "https", hostname: "cdn.myanimelist.net" },
      { protocol: "https", hostname: "lh3.googleusercontent.com" },
    ],
  },
  async rewrites() {
    return [
      // /api/backend/auth/* → backend /auth/* (auth routes are not under /api)
      {
        source: "/api/backend/auth/:path*",
        destination: `${BACKEND_URL}/auth/:path*`,
      },
      // /api/backend/api/* → backend /api/* (path already carries the "api/" segment)
      {
        source: "/api/backend/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
