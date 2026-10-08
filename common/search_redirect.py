# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Forward the global /search route to the datasets search app.

InvenioRDM exposes a global ``/search`` route (backed by ``invenio_search_ui``)
that searches across all registered record metadata models. This repository's
record metadata model ``datasets`` offers its own model-specific search UI
under ``/datasets`` with facets, tips, and a Search guide link consistent with
the rest of this repository.

We replace the global view with a redirect so existing links (bookmarks,
hardcoded ``/search?q=...`` URLs in ``invenio_app_rdm`` JavaScript, external
docs) keep working but land on the datasets UI.
"""

from __future__ import annotations

from flask import Response, redirect, request


def legacy_search_redirect() -> Response:
    """Redirect ``/search?<qs>`` to ``/datasets?<qs>`` preserving the query string."""
    query = request.query_string.decode("utf-8")
    return redirect(f"/datasets?{query}" if query else "/datasets", code=302)
