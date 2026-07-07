#!/usr/bin/env bash
# Upload new images under content/post/ to R2. Incremental — skips existing files.
# Requires: rclone with an [r2] remote configured in ~/.config/rclone/rclone.conf

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
BUCKET="images-blog-cedard-top"

rclone copy "$REPO_ROOT/content/post" "r2:$BUCKET/post" \
  --include "*.jpg" --include "*.JPG" \
  --include "*.jpeg" --include "*.JPEG" \
  --include "*.png" --include "*.PNG" \
  --include "*.gif" --include "*.GIF" \
  --include "*.webp" --include "*.WEBP" \
  --include "*.bmp" --include "*.BMP" \
  --include "*.mov" --include "*.MOV" \
  --include "*.mp4" --include "*.MP4" \
  --transfers 16 \
  --checkers 16 \
  --progress
