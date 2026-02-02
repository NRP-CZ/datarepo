from __future__ import annotations

from ccmm_invenio.models import ccmm_production_preset_1_1_0
from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_model.api import model
from oarepo_model.customizations import PrependMixin
from oarepo_model.model import ModelMixin
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_workflows.model.presets import workflows_preset
from oarepo_model.datatypes.registry import from_yaml


class DatasetsPermissionPolicyMixin(ModelMixin):
    """Custom permission policy for datasets."""

    can_view_deposit_page = [AuthenticatedUser()]


datasets_model = model(
    "datasets",
    version="1.1.0",
    presets=[ccmm_production_preset_1_1_0, workflows_preset, requests_preset],
    types=[from_yaml("record.yaml", __file__), from_yaml("metadata.yaml", __file__)],
    metadata_type="Metadata",
    record_type="Record",
    customizations=[
        # TODO: remove this customization if you use oarepo-communities for RDM 14
        PrependMixin("PermissionPolicy", DatasetsPermissionPolicyMixin),
    ],
    configuration={"ui_blueprint_name": "datasets_ui"},
)
