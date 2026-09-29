#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

case "${1:-all}" in
  all) languages=(ru en cn) ;;
  ru|en|cn|zh) languages=("$1") ;;
  -h|--help) echo "Usage: ./build.sh [all|ru|en|cn|zh]"; exit 0 ;;
  *) echo "Usage: ./build.sh [all|ru|en|cn|zh]" >&2; exit 2 ;;
esac
if (( $# > 1 )); then
  echo "Usage: ./build.sh [all|ru|en|cn|zh]" >&2
  exit 2
fi

command -v hugo >/dev/null || {
  echo "Hugo is required. On Fedora: sudo dnf install hugo" >&2
  exit 1
}
if [[ "$(hugo version)" != *+extended* ]]; then
  echo "Hugo Extended is required by the gallery's SCSS styles." >&2
  exit 1
fi
[[ -f themes/gallery/layouts/partials/head.html ]] || {
  echo "Initialize the theme: git submodule update --init --recursive" >&2
  exit 1
}

for language in "${languages[@]}"; do
  case "$language" in
    ru) domain=akimova.ru ;;
    en) domain=akimova.pro ;;
    cn|zh) domain=akimova.asia ;;
  esac
  echo "==> Building $domain"
  hugo --config "config/$domain.toml" --environment production --cleanDestinationDir --minify
  [[ -s "public/$domain/index.html" && -s "public/$domain/sitemap.xml" ]] || {
    echo "Incomplete build: public/$domain" >&2
    exit 1
  }
done

echo "==> Build complete"
