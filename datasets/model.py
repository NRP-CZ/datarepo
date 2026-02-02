from __future__ import annotations

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
class DatasetsPermissionPolicyMixin(ModelMixin):
    """Custom permission policy for datasets."""

    can_view_deposit_page = [AuthenticatedUser()]

class SetWorkflowInReviewComponent(ServiceComponent):
    def create(self, identity, **kwargs):
        request = kwargs["record"]
        if isinstance(request.type, CommunitySubmission):
            record = request.topic.resolve()
            if record.parent.workflow == "deposition":
                record.parent.workflow = current_oarepo_communities.get_community_default_workflow(
                    community_id=request.receiver._parse_ref_dict_id()).code
            print()



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
