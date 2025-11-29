# ============================================================================
# Stage 1: Dependencies - Install node_modules
# ============================================================================
FROM node:18-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (production + dev for build)
RUN npm ci

# ============================================================================
# Stage 2: Builder - Build Next.js app
# ============================================================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js app (standalone output for minimal size)
RUN npm run build

# ============================================================================
# Stage 3: Runner - Minimal production image
# ============================================================================
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy only necessary files from builder
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Production server (standalone)
CMD ["node", "server.js"]
