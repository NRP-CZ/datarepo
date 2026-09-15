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
                "locations_map": "./js/landing_page/locations_map.js",
                "locations_point": "./js/landing_page/locations_point.js",
                "locations_geometry": "./js/landing_page/locations_geometry.js",
            },
            "dependencies": {
                "leaflet": "^1.9.4",
                "sanitize-html": "2.13.0",
                "@terraformer/wkt": "^2.2.2",
            },
            "devDependencies": {},
            "aliases": {},
        }
    },
)
