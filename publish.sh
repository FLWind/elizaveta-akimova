#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
dry_run=()
case "${1:-}" in
  "") ;;
  --dry-run) dry_run=(--dry-run) ;;
  -h|--help)
    echo "Usage: ./publish.sh [--dry-run]"
    echo "Run ./build.sh first. Syncs all three sites to akimova-ru:, akimova-en: and akimova-cn:."
    exit 0 ;;
  *) echo "Usage: ./publish.sh [--dry-run]" >&2; exit 2 ;;
esac
if (( $# > 1 )); then
  echo "Usage: ./publish.sh [--dry-run]" >&2
  exit 2
fi

command -v rclone >/dev/null || {
  echo "rclone is required. On Fedora: sudo dnf install rclone" >&2
  exit 1
}
command -v python3 >/dev/null || {
  echo "python3 is required to check the build before publishing." >&2
  exit 1
}

# Check ALL sites and remotes before the first sync can modify anything.
python3 "$ROOT/scripts/check_site.py"
remotes="$(rclone listremotes)"
for remote in akimova-ru akimova-en akimova-cn; do
  if ! grep -Fxq -- "$remote:" <<< "$remotes"; then
    echo "Missing rclone remote: $remote. Configure it with rclone config." >&2
    exit 1
  fi
done

for domain in akimova.ru akimova.pro akimova.asia; do
  case "$domain" in
    akimova.ru) remote=akimova-ru ;;
    akimova.pro) remote=akimova-en ;;
    akimova.asia) remote=akimova-cn ;;
  esac
  echo "==> Publishing $domain"
  rclone sync "$ROOT/public/$domain/" "$remote:" \
    --progress --delete-after \
    --exclude '/cgi-bin/**' \
    --exclude '/.well-known/**' \
    "${dry_run[@]}"
done

if (( ${#dry_run[@]} )); then
  echo "==> Dry run complete; no remote files changed"
else
  echo "==> Publish complete"
fi
