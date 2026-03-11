# Documentation deployments

This documentation site has two deployment environments with different configurations.

## Deployment environments

### Public site
- **URL**: https://docs.metadata.lnds.lu/
- **Deployment**: GitLab Pages (manual trigger)
- **Base URL**: `/` (set via `DOCS_BASE_URL=/` in GitLab CI)

### Private site (CDSP)
- **URL**: https://metadata-cdsp.lnds.lu/docs/
- **Deployment**: Docker container with main application
- **Base URL**: `/docs/` (uses default fallback value)

## Configuration

The base URL is configured in `docusaurus.config.ts`:

```typescript
baseUrl: process.env.DOCS_BASE_URL || "/docs/",
```

- **Public site**: GitLab CI sets `DOCS_BASE_URL=/`
- **Private site**: Uses default `/docs/` (no environment variable set)

## Build commands

```bash
# Default build (uses /docs/)
npm run build

# Public site build
DOCS_BASE_URL=/ npm run build

# Private site build (default)
npm run build
```

## Troubleshooting

If you see "Your Docusaurus site did not load properly" with baseUrl errors:

1. Check the `baseUrl` default value in `docusaurus.config.ts`
2. Ensure GitLab CI sets `DOCS_BASE_URL=/` for public deployment
3. Private site should use the default `/docs/` fallback