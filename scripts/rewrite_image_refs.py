#!/usr/bin/env python3
# Rewrite relative image references in markdown files to R2 URLs.
# Idempotent — skips references that are already absolute URLs.

import os
import re
import subprocess
import sys

REPO_ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True
).strip()
CONTENT_DIR = os.path.join(REPO_ROOT, "content", "post")
BASE_URL = "https://images.blog.cedard.top/post"

IMAGE_RE = re.compile(r'!\[([^\]]*)\]\((?!https?://)([^)]+)\)')
FRONTMATTER_RE = re.compile(r'^(image:\s*)(?!https?://)(.+)$', re.MULTILINE)

changed_files = []

for root, dirs, files in os.walk(CONTENT_DIR):
    for fname in files:
        if fname != "index.md":
            continue

        fpath = os.path.join(root, fname)
        rel_dir = os.path.relpath(root, CONTENT_DIR)
        r2_prefix = f"{BASE_URL}/{rel_dir}"

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
        updated = FRONTMATTER_RE.sub(rewrite_fm, updated)

        if updated != original:
            with open(fpath, "w") as f:
                f.write(updated)
            changed_files.append(fpath)
            print(f"  rewritten: {os.path.relpath(fpath, REPO_ROOT)}")

# Print changed files for the hook to stage
for f in changed_files:
    print(f"STAGED:{f}")
