import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker optimization
  output: 'standalone',

  // Enable compression for better performance
  compress: true,

  // Remove X-Powered-By header for security
  poweredByHeader: false,

  // Optimize images
  images: {
    unoptimized: false,
  },

  // Disable ESLint during builds (run separately in CI/CD)
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Disable TypeScript errors during builds (run separately in CI/CD)
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
