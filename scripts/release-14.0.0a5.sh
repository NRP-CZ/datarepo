#!/usr/bin/env bash

# This script prepares a new alpha release.
#

set -exo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
    source .venv/bin/activate
fi

if [ -z "$BUCKET_NAME" ] ; then
    echo "BUCKET_NAME is not set"
    exit 1
fi

if [ -z "$USER_PASSWORD" ]; then
  echo "Error: USER_PASSWORD environment variable is not set."
  exit 1
fi

if [ -z "$KUBERNETES_PORT" ] ; then
    ./run.sh cli services setup
else
    ./run.sh cli services setup --no-services
fi

invenio files location create --default S3 s3://${BUCKET_NAME};


invenio users create -a -c --password "$USER_PASSWORD" admin@test.com
invenio users create -a -c --password "$USER_PASSWORD" user@test.com


invenio roles create administration
invenio access allow administration-access role administration
invenio access allow administration-moderation role administration

invenio roles add admin@test.com administration