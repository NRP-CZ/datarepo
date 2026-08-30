# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
"""Webpack theme bundle for the UI pages."""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "get_access": "./js/get_access/index.js",
            },
            "dependencies": {},
            "aliases": {
                # "@js/datasets": "./js/datasets"
            },
        }
    },
)
