# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""UI resources and Flask app hooks for the datasets model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccmm_invenio.ui.config import CCMMRecordsUIResourceConfig
from ccmm_invenio.ui.resource import CCMMRecordsUIResource
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _
from oarepo_ui.overrides import UIComponent
from oarepo_ui.overrides.components import UIComponentImportMode
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.utils import can_view_deposit_page

if TYPE_CHECKING:
    from flask import Blueprint, Flask


class DatasetsUIResourceConfig(CCMMRecordsUIResourceConfig):
    """Configuration for the DatasetsUIResource."""

    template_folder = "templates"
    url_prefix = "/datasets"
    blueprint_name = "datasets_ui"
    model_name = "datasets"

    search_component = UIComponent(
        "DatasetsResultsListItem",
        "@js/datasets/search/ResultsListItem",
        UIComponentImportMode.DEFAULT,
    )

    components = (*CCMMRecordsUIResourceConfig.components,)

    application_id = "datasets"


class DatasetsUIResource(CCMMRecordsUIResource):
    """A resource for datasets records."""


def ui_overrides(_app: Flask) -> None:
    """Register UI overrides."""
    ui_resource_config = DatasetsUIResourceConfig()

    if (
        current_oarepo_ui is not None
        and ui_resource_config.model
        and ui_resource_config.model.record_json_schema
        and ui_resource_config.search_component
    ):
        current_oarepo_ui.register_result_list_item(
            ui_resource_config.model.record_json_schema,
            ui_resource_config.search_component,
        )


def init_menu(app: Flask) -> None:
    """Initialize menu before first request."""
    ui_resource_config = DatasetsUIResourceConfig()

    with app.app_context():
        current_menu.submenu("plus.create_datasets").register(
            f"{ui_resource_config.blueprint_name}.deposit_create",
            _("New Dataset"),
            order=1,
            visible_when=can_view_deposit_page,
        )
        current_menu.submenu("plus.create_datasets_docs").register(
            "pages_ui.get_access",
            text=_("Get access"),
            order=1,
            visible_when=lambda: not can_view_deposit_page(),
        )
        current_menu.submenu("main.about_repository").register(
            external_url=app.config.get("ABOUT_REPOSITORY_DOCS_URL"),
            text=_("About repository"),
            order=0,
        )


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    init_menu(app)
    ui_overrides(app)


def create_blueprint(_app: Flask) -> Blueprint:
    """Register blueprint for this resource."""
    return DatasetsUIResource(
        DatasetsUIResourceConfig()  # ty: ignore[invalid-argument-type]
    ).as_blueprint()


# TODO: register init_menu to finalize_app similarly blueprints & webpack is registered
