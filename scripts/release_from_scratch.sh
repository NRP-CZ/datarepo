#!/usr/bin/env bash

# This script prepares a new alpha release.
#

set -exo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
    source .venv/bin/activate
fi

if [ -z "$INVENIO_S3_BUCKET" ] ; then
    echo "INVENIO_S3_BUCKET is not set"
    exit 1
fi

if [ -z "$KUBERNETES_SERVICE_HOST" ] ; then
    ./run.sh cli services setup
else
    ./run.sh cli services setup --no-services --no-demo-data
fi

invenio files location create --default s3 s3://${INVENIO_S3_BUCKET};

invenio roles create administration
invenio access allow administration-access role administration
invenio access allow administration-moderation role administration
