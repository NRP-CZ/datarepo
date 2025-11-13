from __future__ import annotations

from ccmm_invenio.models import ccmm_production_preset_1_1_0
from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_model.api import model
from oarepo_model.customizations import AddMixins
from oarepo_model.model import ModelMixin


class DatasetsPermissionPolicyMixin(ModelMixin):
    """Custom permission policy for datasets."""

    can_view_deposit_page = [AuthenticatedUser()]


datasets_model = model(
    "datasets",
    version="1.1.0",
    presets=[ccmm_production_preset_1_1_0],
    types=[],
    metadata_type="CCMMProductionDataset",
    customizations=[
        # TODO: remove this customization if you use oarepo-communities for RDM 14
        AddMixins("PermissionPolicy", DatasetsPermissionPolicyMixin),
    ],
    configuration={"ui_blueprint_name": "datasets_ui"},
)
