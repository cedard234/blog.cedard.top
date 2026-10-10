#!/usr/bin/env python3
# Rewrite relative image references in markdown files to R2 URLs.
# Covers every page bundle under content/ (posts, pages, ...): an image in content/<rel>/ maps to
# https://images.blog.cedard.top/<rel>/, matching the R2 key layout used by upload_to_r2.sh.
# Idempotent — skips references that are already absolute URLs.
# Usage: rewrite_image_refs.py [--dry-run]   (--dry-run: report what would change, write nothing)

import os
import re
import subprocess
import sys

REPO_ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip()
CONTENT_DIR = os.path.join(REPO_ROOT, "content")
BASE_URL = "https://images.blog.cedard.top"
DRY_RUN = "--dry-run" in sys.argv[1:]

IMAGE_RE = re.compile(r'!\[([^\]]*)\]\((?!https?://)([^)]+)\)')
VIDEO_RE = re.compile(r'(<video\b[^>]*\bsrc=")(?!https?://)([^"]+)(")')
FRONTMATTER_RE = re.compile(r'^(image:[ \t]*)(?!https?://)(\S.*)$', re.MULTILINE)  # [ \t]: don't cross into the next line when image: is empty

changed_files = []

for root, dirs, files in os.walk(CONTENT_DIR):
    for fname in files:
        if fname not in ("index.md", "_index.md"):
            continue

        fpath = os.path.join(root, fname)
        rel_dir = os.path.relpath(root, CONTENT_DIR).replace(os.sep, "/")
        r2_prefix = BASE_URL if rel_dir == "." else f"{BASE_URL}/{rel_dir}"

        with open(fpath) as f:
            original = f.read()

        def rewrite_md(m):
            alt, path = m.group(1), m.group(2).strip()
            if path.startswith("http") or path.startswith("/"):
                return m.group(0)
            img_path = path.split()[0].strip('"\'')
            title_suffix = path[len(img_path):]
            return f'![{alt}]({r2_prefix}/{img_path}{title_suffix})'

        def rewrite_fm(m):
            val = m.group(2).strip()
            if val.startswith("http") or val.startswith("/"):
                return m.group(0)
            return f'{m.group(1)}{r2_prefix}/{val}'

        updated = IMAGE_RE.sub(rewrite_md, original)
        def rewrite_video(m):
            src = m.group(2)
            if src.lower().endswith('.mov'):
                src = src[:-4] + '.mp4'
            return f'{m.group(1)}{r2_prefix}/{src}{m.group(3)}'
        updated = VIDEO_RE.sub(rewrite_video, updated)
        updated = FRONTMATTER_RE.sub(rewrite_fm, updated)

        if updated != original:
            if DRY_RUN:
                print(f"  would rewrite: {os.path.relpath(fpath, REPO_ROOT)}")
                continue
            with open(fpath, "w") as f:
                f.write(updated)
            changed_files.append(fpath)
            print(f"  rewritten: {os.path.relpath(fpath, REPO_ROOT)}")

# Print changed files for the hook to stage
for f in changed_files:
    print(f"STAGED:{f}")
