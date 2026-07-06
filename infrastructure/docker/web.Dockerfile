# Build context is the repository root (see docker-compose.yml), because the
# web app resolves @gcol/shared-types from packages/shared via the npm
# workspace.

FROM node:24-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/shared/package.json ./packages/shared/
RUN npm ci

FROM node:24-alpine AS build
WORKDIR /repo
COPY --from=deps /repo/node_modules ./node_modules
COPY package.json package-lock.json ./
COPY apps/web ./apps/web
COPY packages/shared ./packages/shared
# NEXT_PUBLIC_* values are inlined at build time by Next.js, so this is a
# build argument, not a runtime variable.
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN cd apps/web && npm run build

FROM node:24-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs

# No COPY for apps/web/public: the app has no public assets yet, and git
# does not track the empty directory, so the COPY would fail on a fresh
# clone. Restore it when the first real asset lands in public/.
COPY --from=build --chown=nextjs:nodejs /repo/apps/web/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /repo/apps/web/.next/static ./apps/web/.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Uses node's built-in fetch instead of BusyBox wget: wget --spider issues a
# HEAD request that the Next.js standalone server does not answer cleanly, and
# "localhost" can resolve to IPv6 inside Alpine while the server binds IPv4.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/login').then((r) => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "apps/web/server.js"]
