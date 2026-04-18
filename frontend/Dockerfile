# Build stage for Next.js
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY tailwind.config.ts postcss.config.js next.config.ts ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build Next.js app
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install dependencies needed for runtime
RUN npm install -g pm2

# Copy built app from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY  --from=builder /app/package*.json ./
COPY --from=builder /app/next.config.ts ./

# Install runtime dependencies only
RUN npm ci --production

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q -O- http://localhost:3000 || exit 1

# Start Next.js
CMD ["npm", "start"]
