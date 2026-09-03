# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
"""Pages UI resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oarepo_ui.resources import TemplatePageUIResource, TemplatePageUIResourceConfig

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

    def get_access(self) -> str:
        """Render the standalone-submitter onboarding page."""
        return self.render(page="GetAccess")


def create_blueprint(_app: Flask) -> Blueprint:
    """Register blueprint for this resource."""
    return PagesUIResource(
        PagesUIResourceConfig()  # ty: ignore[invalid-argument-type]
    ).as_blueprint()
