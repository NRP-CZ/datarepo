#!/usr/bin/env bash
# Create draft datasets from the sample RO-Crates through the REST API (POST /api/datasets/import/rocrate).
#
#   TOKEN=<personal access token> ./sample_data/import.sh [crate ...]
#
# Without arguments all three samples are imported:
#   sample_rocrate.json       detached crate, metadata only (a metadata-only draft; a detached crate with
#                             files would have them downloaded from their URLs, whose host must be in
#                             RECORDS_RESOURCES_FILES_ALLOWED_DOMAINS)
#   sample_rocrate.zip        attached RO-Crate package - the files are taken from the archive
#   sample_rocrate_bagit.zip  BagIt bag with the RO-Crate - the files are taken from the bag
#
# BASE_URL defaults to the local development server.
set -euo pipefail

: "${TOKEN:?Set TOKEN to a personal access token (invenio tokens create -n <name> -u <email>)}"
BASE_URL="${BASE_URL:-https://127.0.0.1:5000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    set -- "$SCRIPT_DIR/sample_rocrate.json" "$SCRIPT_DIR/sample_rocrate.zip" "$SCRIPT_DIR/sample_rocrate_bagit.zip"
fi

status=0
for crate in "$@"; do
    case "$crate" in
        *.json) content_type="application/ld+json" ;;
        *.zip) content_type="application/zip" ;;
        *) echo "Unknown crate type: $crate (expected .json or .zip)" >&2; status=1; continue ;;
    esac

    echo "Importing $(basename "$crate") ..."
    response=$(curl -sk -w '\n%{http_code}' -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: $content_type" \
        -H "Accept: application/json" \
        --data-binary "@$crate" \
        "$BASE_URL/api/datasets/import/rocrate?notifications=off")
    code=$(tail -n1 <<<"$response")
    body=$(sed '$d' <<<"$response")

    if [[ "$code" == 2* ]]; then
        echo "$body" | jq -r '"  created draft \(.id // .record.id // "?"): \(.links.self_html // .record.links.self_html // .links.self // "")"'
    else
        echo "  failed with HTTP $code:" >&2
        echo "$body" | jq . >&2 2>/dev/null || echo "$body" >&2
        status=1
    fi
done
exit $status
