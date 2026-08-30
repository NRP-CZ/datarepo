# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""fix dates (description needs to be a multilingual dict)"""

import json

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1788084865'
down_revision = '1788081993'
branch_labels = ()
depends_on = None

TABLES = ('datasets_metadata', 'datasets_draft_metadata')
BATCH_SIZE = 1000


def _fix_dates(record_json):
    """Wrap plain-string date descriptions into a {lang, value} dict.

    'lang' is a PIDListRelation to the languages vocabulary (pid_type
    'v-lan'), so it must be a vocabulary reference like {"id": "ENG"},
    not a bare language code - matching how metadata.languages is stored
    elsewhere in this instance (e.g. [{"id": "ENG"}]).
    """
    dates = (record_json.get('metadata') or {}).get('dates')
    if not dates:
        return False
    changed = False
    for date in dates:
        description = date.get('description')
        if isinstance(description, str):
            date['description'] = {'lang': {'id': 'ENG'}, 'value': description}
            changed = True
    return changed


def _unfix_dates(record_json):
    """Reverse _fix_dates: turn {lang, value} dicts back into plain strings."""
    dates = (record_json.get('metadata') or {}).get('dates')
    if not dates:
        return False
    changed = False
    for date in dates:
        description = date.get('description')
        if isinstance(description, dict) and 'value' in description:
            date['description'] = description['value']
            changed = True
    return changed


def _migrate_table(conn, table, fixer):
    """Walk the table in id-ordered batches, so a huge table never loads at once."""
    select_first = sa.text(
        f"SELECT id, json FROM {table} "  # noqa: S608
        "WHERE json -> 'metadata' -> 'dates' IS NOT NULL "
        "ORDER BY id LIMIT :limit"
    )
    select_next = sa.text(
        f"SELECT id, json FROM {table} "  # noqa: S608
        "WHERE json -> 'metadata' -> 'dates' IS NOT NULL AND id > :last_id "
        "ORDER BY id LIMIT :limit"
    )
    update = sa.text(f"UPDATE {table} SET json = :json WHERE id = :id")  # noqa: S608

    last_id = None
    while True:
        stmt, params = (
            (select_first, {'limit': BATCH_SIZE})
            if last_id is None
            else (select_next, {'last_id': last_id, 'limit': BATCH_SIZE})
        )
        batch = conn.execute(stmt, params).fetchall()
        if not batch:
            break
        for row in batch:
            data = row.json
            if fixer(data):
                conn.execute(update, {'json': json.dumps(data), 'id': row.id})
            last_id = row.id


def _migrate(fixer):
    conn = op.get_bind()
    for table in TABLES:
        _migrate_table(conn, table, fixer)


def upgrade():
    """Upgrade database."""
    _migrate(_fix_dates)


def downgrade():
    """Downgrade database."""
    _migrate(_unfix_dates)
