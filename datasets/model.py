from __future__ import annotations

from ccmm_invenio.models import ccmm_production_preset_1_1_0
from invenio_rdm_records.resources.serializers.ui.schema import UIRecordSchema
from oarepo_communities.model.presets import communities_preset
from oarepo_model.api import model
from oarepo_model.customizations import (
    AddFacetGroup,
    PatchIndexMapping,
    PatchIndexPropertyMapping,
    PatchIndexSettings,
    PrependMixin,
    SetDefaultSearchFields,
)
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_workflows.model.presets import workflows_preset

COPY_TO_MAPPINGS = [
    # boost_10 - Primary identifiers (highest weight)
    ("metadata.title", 10),
    ("id", 10),
    # boost_5 - Important searchable content
    ("metadata.additional_titles.title", 5),
    ("metadata.creators.person_or_org.name", 5),
    # Author names
    # boost_1 - Supplementary content
    ("metadata.additional_descriptions.description", 1),
    ("metadata.contributors.person_or_org.name", 1),
    # Contributor names
    ("metadata.publisher", 1),
    # Publisher
    ("metadata.funding.funder.name", 1),
    # Funder names
]

copy_to_mappings = [
    PatchIndexPropertyMapping(c[0], {"copy_to": f"boost_{c[1]}"})
    for c in COPY_TO_MAPPINGS
]
analyzer_fields = {
    "fields": {
        # using both means that queries that match both ascii and non-ascii
        # versions are ranked higher (if query is Novák, records with Novák
        # will have better ranking than Novak and both will be found),
        # but if user searches for Novak Novák will still match with
        # lower ranking than Novak
        "_search": {"type": "text", "analyzer": "lowercase_analyzer"},
        "_ascii_search": {
            "type": "text",
            "analyzer": "asciifolded_lowercase_analyzer",
        },
    }
}


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
        AddFacetGroup(
            "default",
            facets=[
                "metadata.resource_type",
                "metadata.publisher",
                "metadata.creators.affiliations",
                "metadata.subjects.subject",
                "metadata.funding.funder",
                "metadata.languages",
                "metadata.rights",
            ],
        ),
        # index tweaks
        PatchIndexSettings(
            {
                "analysis": {
                    # lowercase splits on whitespaces and performs lowercasing
                    "tokenizer": {"lowercase_tokenizer": {"type": "lowercase"}},
                    "analyzer": {
                        "lowercase_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase_tokenizer",
                        },
                        "asciifolded_lowercase_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase_tokenizer",
                            # additionally removes diacritics
                            "filter": ["asciifolding"],
                        },
                    },
                }
            }
        ),
        PatchIndexMapping(
            {
                "properties": {
                    "boost_10": {"type": "text", "boost": 10, **analyzer_fields},
                    "boost_5": {"type": "text", "boost": 5, **analyzer_fields},
                    "boost_1": {"type": "text", "boost": 1, **analyzer_fields},
                    "parent.is_harvested": {"type": "boolean"},
                }
            }
        ),
        *copy_to_mappings,
        SetDefaultSearchFields(
            "boost_10",
            "boost_5",
            "boost_1",
            "boost_10._search",
            "boost_5._search",
            "boost_1._search",
            "boost_10._ascii_search",
            "boost_5._ascii_search",
            "boost_1._ascii_search",
        ),
    ],
    configuration={"ui_blueprint_name": "datasets_ui"},
)
