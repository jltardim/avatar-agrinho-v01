const nextConfig = {
  experimental: {
    turbo: {
      // Fix Turbopack root to this project to avoid multi-lockfile inference issues
      root: __dirname,
    },
  },
} satisfies import("next").NextConfig;

export default nextConfig;
