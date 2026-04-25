#!/bin/sh
set -eu

version="${1:-}"

if [ -z "$version" ]; then
  echo "Missing version argument."
  exit 1
fi

version="${version#v}"

if ! printf '%s\n' "$version" | grep -E -q '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z][0-9A-Za-z.-]*)?(\+[0-9A-Za-z][0-9A-Za-z.-]*)?$'; then
  echo "Invalid SemVer version: $version"
  exit 1
fi

tmp_file="VERSION.tmp"

printf '%s\n' "$version" > "$tmp_file"
mv "$tmp_file" VERSION

echo "Updated VERSION to $version"
