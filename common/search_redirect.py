# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Legacy /search view: forward to the datasets search app.

OARepo registers a model-specific search UI under ``/datasets``. InvenioRDM
also exposes a generic ``/search`` endpoint backed by ``invenio_search_ui``
that uses the legacy RDM search app without facets / tips matching this
repository. We replace that view with a permanent redirect so all existing
links (bookmarks, hardcoded ``/search?q=...`` URLs in ``invenio_app_rdm``
JavaScript, external docs) keep working but land on the datasets UI.
"""

from __future__ import annotations

from flask import redirect, request


def legacy_search_redirect():
    """Redirect ``/search?<qs>`` to ``/datasets?<qs>`` preserving the query string."""
    query = request.query_string.decode("utf-8")
    return redirect(f"/datasets?{query}" if query else "/datasets", code=302)
