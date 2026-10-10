#!/usr/bin/env bash
# Upload new media under content/ (posts, pages, ...) to R2. Incremental — skips existing files.
# content/<rel>/file maps to r2:<bucket>/<rel>/file, e.g. content/post/x/a.png -> post/x/a.png.
# Requires: rclone with an [r2] remote configured in ~/.config/rclone/rclone.conf
# Extra arguments are passed to rclone, e.g.  upload_to_r2.sh --dry-run

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
BUCKET="images-blog-cedard-top"

rclone copy "$REPO_ROOT/content" "r2:$BUCKET" \
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
  --progress \
  "$@"
