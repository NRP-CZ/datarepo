#!/usr/bin/env bash

# This script reconstructs the search index for all records.
#

set -exo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
    source .venv/bin/activate
fi

invenio index destroy --yes-i-know
invenio index init
invenio rdm-records custom-fields init
invenio communities custom-fields init
invenio rdm-records rebuild-index
invenio rdm rebuild-all-indices