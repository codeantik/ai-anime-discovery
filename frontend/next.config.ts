import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8001";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "*.anilist.co" },
      { protocol: "https", hostname: "cdn.myanimelist.net" },
    ],
  },
  async rewrites() {
    return [
      // /api/backend/auth/mal/* → backend /auth/mal/* (not under /api)
      {
        source: "/api/backend/auth/:path*",
        destination: `${BACKEND_URL}/auth/:path*`,
      },
      // /api/backend/* → backend /api/*
      {
        source: "/api/backend/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
