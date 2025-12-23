# Frontend Dockerfile for SHERPA Dashboard
# Multi-stage build for production-optimized React + Vite application

# Stage 1: Builder - Install dependencies and build the application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production --ignore-scripts

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production - Serve the built application
FROM node:20-alpine AS production

# Install serve globally for serving static files
RUN npm install -g serve

# Create non-root user
RUN addgroup -g 1000 sherpa && \
    adduser -D -u 1000 -G sherpa sherpa

# Set working directory
WORKDIR /app

# Copy built files from builder stage
COPY --from=builder --chown=sherpa:sherpa /app/dist ./dist
COPY --from=builder --chown=sherpa:sherpa /app/package.json ./

# Switch to non-root user
USER sherpa

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001 || exit 1

# Start the application
CMD ["serve", "-s", "dist", "-l", "3001"]
