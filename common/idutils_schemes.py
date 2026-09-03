# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Custom idutils schemes for ORJK identifiers and parent record ids."""

from __future__ import annotations

import re
from typing import Any

_ORJK_RE = re.compile(r"^orjk:", re.IGNORECASE)


def is_orjk(value: Any) -> bool:
    """Return True if the value looks like an ORJK identifier."""
    return isinstance(value, str) and _ORJK_RE.match(value.strip()) is not None


def is_parent_id(_value: Any) -> bool:
    """Return True for any value: parent ids are not further validated."""
    return True


def normalize_orjk(value: str) -> str:
    """Normalize an ORJK identifier to lower case."""
    return value.strip().lower()


def normalize_parent_id(value: Any) -> Any:
    """Normalize a parent id to lower case, leaving non-strings untouched."""
    return value.strip().lower() if isinstance(value, str) else value


def orjk_scheme() -> dict:
    """Return the idutils scheme definition for ORJK identifiers."""
    return {
        "validator": is_orjk,
        "normalizer": normalize_orjk,
    }


def parent_id_scheme() -> dict:
    """Return the idutils scheme definition for parent record ids."""
    return {
        "validator": is_parent_id,
        "normalizer": normalize_parent_id,
    }
