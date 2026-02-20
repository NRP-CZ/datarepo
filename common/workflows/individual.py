from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions
from oarepo_workflows.requests.policy import WorkflowRequestPolicy
from oarepo_workflows.requests.requests import WorkflowRequest

class IndividualDepositionWorkflowPermissions(DefaultWorkflowPermissions):
    can_create = [AuthenticatedUser()]
    can_review = [AuthenticatedUser()] # for link creation
