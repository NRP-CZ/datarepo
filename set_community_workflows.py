# this file needs to be run with invenio shell <filename>
from typing import cast

from invenio_db import db
from invenio_communities.communities.records.models import CommunityMetadata
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from sqlalchemy.orm.attributes import flag_modified
from oarepo_runtime.proxies import current_runtime
from invenio_rdm_records.records.models import RDMDraftMetadata, RDMParentMetadata, RDMRecordMetadata

def set_community_workflows():
    with db.session.begin_nested():
        communities = db.session.query(CommunityMetadata).all()
        for community in communities:
            if "workflow" in community.json.get("custom_fields"):
                continue
            community.json["custom_fields"] = {
                "workflow": "community",
                "allowed_workflows": ["community"]
            }
            flag_modified(community, "json")

            db.session.add(community)
    db.session.commit()

def set_record_workflows():
    record_cls = cast("RDMRecord", current_runtime.models["datasets"].record_cls)
    draft_cls = cast("RDMDraft", current_runtime.models["datasets"].draft_cls)

    parent: RDMParentMetadata
    rec: RDMRecordMetadata | RDMDraftMetadata
    with db.session.begin_nested():
        for rec in db.session.query(record_cls.model_cls).all():
            parent = rec.parent
            parent_json = cast(dict, parent.json)
            if parent_json.get("communities"):
                expected_workflow = "community"
            else:
                expected_workflow = "individual"
            parent.workflow = expected_workflow
            db.session.add(parent)

        for rec in db.session.query(draft_cls.model_cls).all():
            parent = rec.parent
            parent_json = cast(dict, parent.json)
            if parent is not None and "workflow" not in parent_json:
                if parent_json.get("communities"):
                    expected_workflow = "community"
                else:
                    expected_workflow = "individual"
                parent.workflow = expected_workflow
                db.session.add(parent)
    db.session.commit()


set_community_workflows()
set_record_workflows()
