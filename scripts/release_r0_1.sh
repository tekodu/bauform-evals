#!/usr/bin/env bash
set -euo pipefail
tag="r0.1-$(date +%Y%m%d)"
rm -f SHA256SUMS
# suite index + all bundles
sha256sum r0.1/suite.index.json.signed > SHA256SUMS
for b in r0.1/*/result.json.signed; do sha256sum "$b" >> SHA256SUMS; done
git add -A
git commit -m "r0.1 artifacts + SHA256SUMS"
git tag -a "$tag" -m "Bauform r0.1 signed artifacts"
git push origin main --tags
# Note: gh release create requires GitHub CLI - run manually if needed
# gh release create "$tag" -F SHA256SUMS r0.1/suite.index.json.signed $(ls r0.1/*/result.json.signed)
echo "✅ Release $tag ready. Create GitHub release manually with SHA256SUMS and signed artifacts."

