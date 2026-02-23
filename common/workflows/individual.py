from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions


class IndividualDepositionWorkflowPermissions(DefaultWorkflowPermissions):
    can_create = [AuthenticatedUser()]
    can_manage_files = [AuthenticatedUser()]
