#!/bin/bash

# Bump version in __init__.py and create a git commit + tag.

# Usage:
# ./bump_version.sh [major|minor|patch]
# Default: patch

file="calico_lib/__init__.py"
part="${1:-patch}"

if [[ ! -f "$file" ]]; then
  echo "Error: '$file' not found in the current directory."
  exit 1
fi

# Extract version
version=$(grep -oP '__version__ = "\K[0-9]+\.[0-9]+\.[0-9]+' "$file")

if [[ -z "$version" ]]; then
  echo "Error: Could not find __version__ in $file"
  exit 1
fi

IFS='.' read -r major minor patch <<< "$version"

case "$part" in
  major)
    major=$((major + 1))
    minor=0
    patch=0
    ;;
  minor)
    minor=$((minor + 1))
    patch=0
    ;;
  patch)
    patch=$((patch + 1))
    ;;
  *)
    echo "Error: Unknown part '$part' (use: major, minor, patch)"
    exit 1
    ;;
esac

new_version="${major}.${minor}.${patch}"

# Replace version in __init__.py
sed -E -i "s/(__version__ = \")[0-9]+\.[0-9]+\.[0-9]+\"/\1${new_version}\"/" "$file"

# Git commit and tag
git add "$file"
git commit -m "chore: bump version to ${new_version}"
git tag "v${new_version}"

echo "✅ Version updated: $version → $new_version"
echo "✅ Git tag created: v${new_version}"
echo "TODO:"
echo "Run 'git push -t' to push"
echo "Run 'flit publish' to publish"
