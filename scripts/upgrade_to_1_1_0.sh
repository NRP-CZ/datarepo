#!/usr/bin/env bash
#
# Upgrades the datarepo instance to version 1.1.0
#
# Usage (invenio command must be available):
#   ./upgrade_to_1_1_0.sh

# upgrade the database schema
invenio alembic upgrade heads

# re-create the index
invenio index destroy --yes-i-know
invenio index queue init purge
invenio index init
invenio rdm-records custom-fields init
invenio communities custom-fields init
invenio queues declare

# re-index the records
invenio rdm rebuild-all-indices
