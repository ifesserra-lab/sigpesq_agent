---
description: Bump the project version using SemVer rules
---

To increment the project version (major, minor, or patch), follow the CI/CD Tagging process:

// turbo
1. Create and Push Tag:
```bash
# Example for v0.2.3
git tag v0.2.3
git push origin v0.2.3
```
*Note: The GitHub Action will handle the actual version bump in `pyproject.toml` and publishing.*
