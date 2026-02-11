from __future__ import annotations

from typing import TYPE_CHECKING, override
from oarepo_workflows.errors import MissingWorkflowError
from oarepo_workflows.services.permissions import FromRecordWorkflow
from oarepo.config.communities import DefaultCommunitiesPermissionPolicy
from oarepo_communities.proxies import current_oarepo_communities
from invenio_records_permissions.generators import SystemProcess, AuthenticatedUser

if TYPE_CHECKING:
    from typing import Any
    from invenio_drafts_resources.records import Record
    from oarepo_workflows import Workflow


class DepositionWorkflowPermission(FromRecordWorkflow):


    @override
    def _get_workflow(self, record: Record | None = None, **context: Any) -> Workflow:
        # TODO: implement use for all workflows, skipping for now
        workflow = current_oarepo_communities.get_community_default_workflow(**context | {"record": record})
        if not workflow:
            raise MissingWorkflowError("Workflow not defined in input.")
        return workflow


class DataSetsCommunitiesPermission(DefaultCommunitiesPermissionPolicy):
    # called during community-submission submit request
    # and in invenio_communities.communities.resources.ui_schema.UICommunitySchema.get_permissions; in community search at least
    can_submit_record = [SystemProcess(), AuthenticatedUser()]

