# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
"""Support for Ark for the older records."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from oarepo_ark.handlers.rdm import RDMRecordHandler

if TYPE_CHECKING:
    from invenio_records.api import Record


class DataRepoArkHandler(RDMRecordHandler):
    """Ark handler that converts structural characters in old catchall repository to Ark-safe characters."""

    @override
    def get_blade(self, record: Record) -> str:
        blade = super().get_blade(record)
        if blade.startswith("datst."):
            return f"datst-{blade[6:]}"
        return blade
