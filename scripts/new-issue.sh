#!/usr/bin/env bash
# Create an issue on the Brewmaster board.
#
#   ./scripts/new-issue.sh "Title" "Body, including acceptance criteria"
#
# Needs FORGE_URL, FORGE_TOKEN and FORGE_REPO exported. Get a token from
# Forgejo under Settings -> Applications -> Generate New Token.
set -euo pipefail

: "${FORGE_URL:?set FORGE_URL, e.g. http://forge.lan:3000}"
: "${FORGE_TOKEN:?set FORGE_TOKEN}"
: "${FORGE_REPO:?set FORGE_REPO, e.g. brewteam/brewmaster}"

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <title> <body>" >&2
  exit 64
fi

curl -sS -X POST "$FORGE_URL/api/v1/repos/$FORGE_REPO/issues" \
  -H "Authorization: token $FORGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg t "$1" --arg b "$2" '{title: $t, body: $b}')" \
  | jq -r '"created #\(.number): \(.title)\n\(.html_url)"'
