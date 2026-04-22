from invenio_rdm_records.services.generators import RecordOwners
from invenio_records_permissions.generators import AuthenticatedUser
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions


class IndividualDepositionWorkflowPermissions(DefaultWorkflowPermissions):
    can_create = [AuthenticatedUser()]
    can_review = [AuthenticatedUser()]  # for link creation
    can_manage = [RecordOwners()]
