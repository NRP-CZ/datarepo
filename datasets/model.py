from __future__ import annotations

from typing import cast

from oarepo_runtime import current_runtime
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from oarepo_model.customizations.high_level import AddServiceComponent
from invenio_rdm_records.services.services import RDMRecordService
from ccmm_invenio.models import ccmm_production_preset_1_1_0
from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_model.api import model
from oarepo_model.customizations import PrependMixin
from oarepo_model.model import ModelMixin
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_workflows.model.presets import workflows_preset
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_communities.model.presets import communities_preset
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from oarepo_communities.proxies import current_oarepo_communities
class DatasetsPermissionPolicyMixin(ModelMixin):
    """Custom permission policy for datasets."""

    can_view_deposit_page = [AuthenticatedUser()]

datasets_model = model(
    "datasets",
    version="1.1.0",
    presets=[ccmm_production_preset_1_1_0, workflows_preset, requests_preset, communities_preset],
    types=[],
    metadata_type="CCMMDataset",
    customizations=[
        # TODO: remove this customization if you use oarepo-communities for RDM 14
        PrependMixin("PermissionPolicy", DatasetsPermissionPolicyMixin),
    ],
    configuration={"ui_blueprint_name": "datasets_ui"},
)
