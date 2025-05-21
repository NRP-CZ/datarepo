#!/bin/bash

#
# Usage:
# export USER_PASSWORD=<your_password>
# export BUCKET_NAME=<your_bucket_name>
# ./scripts/initialize.sh [--destroy]
#
#

set -e
set -o pipefail

cd "$(dirname $0)/.."

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --destroy) DESTROY=true ;;
        *) echo "Unknown parameter passed: $1. Usage: $0 [--destroy]"; exit 1 ;;
    esac
    shift
done

export DESTROY

if [ -d .venv ]; then
    source .venv/bin/activate
fi

if [ -z "$USER_PASSWORD" ] ; then
    echo "USER_PASSWORD is not set"
    exit 1
fi

if [ -z "$BUCKET_NAME" ] ; then
    echo "BUCKET_NAME is not set"
    exit 1
fi

if [ "$DESTROY" == "true" ] ; then
    invenio db destroy --yes-i-know || true
    invenio index destroy --force --yes-i-know || true
    invenio db init create 
    invenio index init
fi

invenio oarepo cf init
invenio communities custom-fields init
invenio files location create --default default s3://${BUCKET_NAME};

invenio oarepo fixtures load --batch-size 1000 --verbose
invenio oarepo fixtures load --no-system-fixtures ./fixtures --batch-size 1000 --verbose
invenio oarepo vocabularies import-ror


invenio users create -a -c nrdocstest+datapilot@gmail.com --password ${USER_PASSWORD} --profile '{"full_name": "Správce datového pilota"}'
invenio oarepo communities members add generic "nrdocstest+datapilot@gmail.com" owner
invenio access allow administration-access user nrdocstest+datapilot@gmail.com
invenio access allow administration-moderation user nrdocstest+datapilot@gmail.com

# invenio oarepo vocabularies import-ror

invenio oarepo index reindex
invenio oarepo index reindex
