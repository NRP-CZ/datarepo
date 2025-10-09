from oarepo_ui.resources import BabelComponent
from oarepo_ui.resources.components import (
    # AllowedCommunitiesComponent,
    AllowedHtmlTagsComponent,
    EmptyRecordAccessComponent,
    FilesComponent,
    FilesLockedComponent,
    FilesQuotaAndTransferComponent,
    RecordRestrictionComponent,
    PermissionsComponent,
)
from oarepo_ui.resources.components.custom_fields import CustomFieldsComponent
from oarepo_ui.resources.records.config import RecordsUIResourceConfig
from oarepo_ui.resources.records.resource import RecordsUIResource
from oarepo_ui.utils import can_view_deposit_page
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _
from oarepo_ui.overrides import UIComponent
from oarepo_ui.overrides.components import UIComponentImportMode
from oarepo_ui.proxies import current_oarepo_ui

class DatasetsUIResourceConfig(RecordsUIResourceConfig):
    template_folder = "templates"
    url_prefix = "/datasets"
    blueprint_name = "datasets_ui"
    model_name = "datasets"

    search_component = UIComponent(
        "DatasetsResultsListItem",
        "@js/datasets/search/ResultsListItem",
        UIComponentImportMode.DEFAULT
    )

    components = [
        AllowedHtmlTagsComponent,
        BabelComponent,
        PermissionsComponent,
        FilesComponent,
        # AllowedCommunitiesComponent,
        CustomFieldsComponent,
        RecordRestrictionComponent,
        EmptyRecordAccessComponent,
        FilesLockedComponent,
        FilesQuotaAndTransferComponent,
    ]
    
    try:
        from oarepo_vocabularies.ui.resources.components import (
            DepositVocabularyOptionsComponent,
        )
        components.append(DepositVocabularyOptionsComponent)
    except ImportError:
        pass

    application_id = "datasets"
 
    templates = {
        "record_detail": "datasets.RecordDetail",
        "search": "datasets.Search",
        "deposit_edit": "datasets.Deposit",
        "deposit_create": "datasets.Deposit",
    }


class DatasetsUIResource(RecordsUIResource):
    pass

def ui_overrides(app):
    """Register UI overrides."""
    ui_resource_config = DatasetsUIResourceConfig()

    if (
        current_oarepo_ui is not None
        and ui_resource_config.model
        and ui_resource_config.model.record_json_schema
        and ui_resource_config.search_component
    ):
        current_oarepo_ui.register_result_list_item(
            ui_resource_config.model.record_json_schema, ui_resource_config.search_component
        )


def init_menu(app):
    """Initialize menu before first request."""
    ui_resource_config = DatasetsUIResourceConfig()

    with app.app_context():
        current_menu.submenu("plus.create_datasets").register(
            f"{ui_resource_config.blueprint_name}.deposit_create",
            _("New Datasets"),
            order=1,
            visible_when=can_view_deposit_page,
        )

def finalize_app(app):
    """Finalize app"""
    init_menu(app)
    ui_overrides(app)

def create_blueprint(app):
    """Register blueprint for this resource."""
    blueprint = DatasetsUIResource(DatasetsUIResourceConfig()).as_blueprint()
    return blueprint

# TODO: register init_menu to finalize_app similarly blueprints & webpack is registered