from __future__ import annotations

from ccmm_invenio.models import ccmm_production_preset_1_1_0
from invenio_rdm_records.resources.serializers.ui.schema import UIRecordSchema
from oarepo_communities.model.presets import communities_preset
from oarepo_model.api import model
from oarepo_model.customizations import PrependMixin
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_workflows.model.presets import workflows_preset

datasets_model = model(
    "datasets",
    version="1.1.0",
    presets=[
        ccmm_production_preset_1_1_0,
        workflows_preset,
        requests_preset,
        communities_preset,
    ],
    types=[],
    metadata_type="CCMMDataset",
    customizations=[
        PrependMixin("RecordUISchema", UIRecordSchema),
    ],
    configuration={"ui_blueprint_name": "datasets_ui"},
)
