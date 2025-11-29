# ============================================================================
# Stage 1: Builder - Build TypeScript
# ============================================================================
FROM node:18-alpine AS builder

WORKDIR /build

# Copy package files
COPY package*.json tsconfig.json ./

# Install ALL dependencies (including dev for TypeScript)
RUN npm ci

# Copy source code
COPY src ./src

# Build TypeScript
RUN npm run build

# ============================================================================
# Stage 2: Runner - Minimal production image
# ============================================================================
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 proxyuser

# Copy package files
COPY package*.json ./

# Install ONLY production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy built JavaScript from builder
COPY --from=builder --chown=proxyuser:nodejs /build/dist ./dist

# Switch to non-root user
USER proxyuser

EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:9000/health || exit 1

# Production server
CMD ["node", "dist/server.js"]

