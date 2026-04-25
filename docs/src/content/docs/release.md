---
title: Release process
description: How release tags publish signed Docker images and GitHub notes.
---

Releases are driven by Git tags in the format `v*.*.*` (example: `v1.2.3`).

## What happens on release

When a release tag is pushed, GitHub Actions will:

1. Validate Python source compiles.
2. Build and push a multi-arch Docker image to Docker Hub.
3. Generate SBOM and provenance attestation.
4. Sign image using Cosign keyless signing (OIDC).
5. Create GitHub Release notes automatically.

## Published image tags

- `X.Y.Z`
- `X`
- `latest` (only when release is from default branch)

## Image location

The published image is configured by release workflow secrets:

```text
docker.io/<DOCKERHUB_USERNAME>/<DOCKERHUB_REPOSITORY>
```

The provided Docker Compose file currently uses:

```text
zen-mcp/browser:${BROWSER_MCP_TAG}
```
