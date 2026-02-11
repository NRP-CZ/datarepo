from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions
from oarepo_workflows.requests.policy import WorkflowRequestPolicy
from oarepo_workflows.requests.requests import WorkflowRequest

class IndividualDepositionWorkflowPermissions(DefaultWorkflowPermissions):
    can_create = [AuthenticatedUser()]

class IndividualDepositionWorkflowRequestsPermissions(WorkflowRequestPolicy):
    # recipient is decided in the review service
    # permission check for request creation in workflows based on actual record community is doable by modifying FromRecordWorkflow to use receiver (community) instead of record (it's poped out from data and resolved in invenio code)
    community_submission = WorkflowRequest(
        requesters=[
            AuthenticatedUser()
        ],
        recipients=[],
    )
