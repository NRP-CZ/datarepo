# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
"""Webpack theme bundle for the datasets UI."""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(  # noqa C408 invenio convention
            entry={
                "datasets_search": "./js/datasets/search/index.js",
                "datasets_deposit_form": "./js/datasets/forms/index.js",
            },
            dependencies={},
            # TODO: pinned less dependency, because in version 4.6 of less, they are using exclusively ES modules
            # and less loader is using require
            devDependencies={"less": "4.5.1"},
            aliases={"@js/datasets": "./js/datasets"},
        )
    },
)
