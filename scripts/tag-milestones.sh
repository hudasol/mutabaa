#!/usr/bin/env bash
# Creates the milestone tags listed in CHANGELOG.md at the commits recorded in scripts/milestones.txt,
# then pushes them. Run from the repository root on a machine where `git push --tags` is allowed.
# (The build environment that produced this repository could not push tags.)
set -euo pipefail

while read -r tag sha; do
  [ -z "${tag:-}" ] && continue
  case "$tag" in \#*) continue ;; esac
  if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    echo "exists: $tag"
  else
    git tag -a "$tag" "$sha" -m "$tag"
    echo "tagged: $tag -> $sha"
  fi
done < scripts/milestones.txt

git push origin --tags
