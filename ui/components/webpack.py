# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Webpack theme bundle for shared UI components."""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "components": "./js/custom-components.js",
            },
            "dependencies": {},
            "devDependencies": {},
            "aliases": {},
        }
    },
)
