# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
"""Pages UI resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import redirect, url_for
from flask_security import login_required
from oarepo_ui.resources import TemplatePageUIResource, TemplatePageUIResourceConfig
from oarepo_ui.utils import can_view_deposit_page
from werkzeug import Response

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask import Blueprint, Flask


class PagesUIResourceConfig(TemplatePageUIResourceConfig):
    """Configuration for the PagesUIResource."""

    template_folder = "templates"
    url_prefix = "/"
    blueprint_name = "pages_ui"
    application_id = "pages"

    pages: Mapping[str, str] = {"get-access": "GetAccess"}


class PagesUIResource(TemplatePageUIResource):
    """A resource for rendering jinja template pages with a specific configuration."""

    def create_url_rules(self) -> list:
        """Route /get-access to a semantic handler name."""
        from flask_resources import route

        return [route("GET", "get-access", self.get_access)]

    @login_required
    def get_access(self) -> str | Response:
        """Render the standalone-submitter onboarding page.

        Users who already have deposition permission are redirected
        straight to the deposit page.
        """
        if can_view_deposit_page():
            return redirect(url_for("datasets_ui.deposit_create"))
        return self.render(page="GetAccess")


def create_blueprint(_app: Flask) -> Blueprint:
    """Register blueprint for this resource."""
    return PagesUIResource(
        PagesUIResourceConfig()  # ty: ignore[invalid-argument-type]
    ).as_blueprint()
