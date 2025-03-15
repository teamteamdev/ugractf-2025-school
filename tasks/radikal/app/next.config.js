/** @type {import('next').NextConfig} */

const basePath = process.env.BASE_PATH ?? '';

const nextConfig = {
  // Configure static file serving from the uploads directory
  async rewrites() {
    return [
      {
        source: '/uploads/:path*',
        destination: '/uploads/:path*',
      },
    ];
  },
  basePath,
  env: {
    basePath,
  },
  output: "standalone",
  compress: false,
}

module.exports = nextConfig
