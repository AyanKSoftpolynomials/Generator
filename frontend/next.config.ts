import type { NextConfig } from "next";

// The Python API (python -m backend). The browser only ever talks to this
// Next.js origin; /api/* is proxied server-side.
const API_URL = process.env.LMS_API_URL ?? "http://127.0.0.1:8765";

const nextConfig: NextConfig = {
  experimental: {
    // Default is 30 s. Analyzing a big lesson the first time (every MathTex
    // compiled by LaTeX) can take over a minute; don't cut it off.
    proxyTimeout: 15 * 60 * 1000,
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/api/:path*` }];
  },
};

export default nextConfig;
