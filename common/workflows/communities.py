from __future__ import annotations

from typing import TYPE_CHECKING, override
from oarepo_workflows.errors import MissingWorkflowError
from oarepo_workflows.services.permissions import FromRecordWorkflow
from oarepo.config.communities import DefaultCommunitiesPermissionPolicy
from oarepo_communities.proxies import current_oarepo_communities
from invenio_records_permissions.generators import SystemProcess
if TYPE_CHECKING:
    from typing import Any
    from invenio_drafts_resources.records import Record
    from oarepo_workflows import Workflow


class DepositionWorkflowPermission(FromRecordWorkflow):


    @override
    def _get_workflow(self, record: Record | None = None, **context: Any) -> Workflow:
        # workflow = super()._get_workflow(record=record, **context) # TODO: record is community; we need to change the service to send the real record here
        # if workflow.code == "deposition":
        workflow = current_oarepo_communities.get_community_default_workflow(**context)
        if not workflow:
            raise MissingWorkflowError("Workflow not defined in input.")
        return workflow


class DataSetsCommunitiesPermission(DefaultCommunitiesPermissionPolicy):
    can_submit_record = [SystemProcess(), DepositionWorkflowPermission("create")]

