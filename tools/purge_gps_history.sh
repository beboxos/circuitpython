#!/usr/bin/env bash
#
# purge_gps_history.sh - remove the old photos that carried GPS coordinates
# from the WHOLE git history.
#
# Two Seeed XIAO photos used to embed GPS location in their EXIF metadata. The
# current versions in the working tree are clean, but the originals are still
# reachable in old commits. This script rewrites history to drop those blobs.
#
# ⚠️  THIS REWRITES HISTORY. It is intentionally NOT run by CI and must be run
#     by the repository owner, on a fresh clone, then force-pushed:
#
#       git clone https://github.com/beboxos/circuitpython
#       cd circuitpython
#       bash tools/purge_gps_history.sh
#       # inspect the result, then:
#       git push --force --all
#       git push --force --tags
#
# Everyone with an existing clone must then re-clone (or reset --hard) because
# the commit hashes change. Requires git-filter-repo:
#       pip install git-filter-repo
#
set -euo pipefail

if ! command -v git-filter-repo >/dev/null 2>&1 && \
   ! python3 -c "import git_filter_repo" >/dev/null 2>&1; then
  echo "git-filter-repo is required:  pip install git-filter-repo" >&2
  exit 1
fi

# The paths to purge from every commit (current clean copies are re-added by
# the commit that introduced the scrubbed versions).
PATHS=(
  "Seeed XIAO/UartToHID/images/20210923_221442.jpg"
  "Seeed XIAO/UartToHID/images/20210923_221620.jpg"
)

ARGS=()
for p in "${PATHS[@]}"; do
  ARGS+=(--path "$p")
done

echo "Rewriting history to strip the GPS photos from all commits..."
git filter-repo --invert-paths "${ARGS[@]}" --force

cat <<'NOTE'

Done. The GPS-bearing blobs are gone from history.

The current (clean, no-GPS) images were removed too, so re-add them:

  git checkout <this-branch> -- "Seeed XIAO/UartToHID/images/"   # if needed
  git add "Seeed XIAO/UartToHID/images/"
  git commit -m "re-add scrubbed Seeed XIAO photos (no EXIF/GPS)"

Then force-push (see the header of this script) and tell collaborators to
re-clone.
NOTE
