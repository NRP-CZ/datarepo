from invenio_rdm_records.requests.entity_resolvers import RDMRecordServiceResultProxy
from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)
from oarepo_requests.resolvers.service_result import DraftServiceResultResolver
from oarepo_requests.resolvers.ui import (
    RecordEntityDraftReferenceUIResolver,
    RecordEntityReferenceUIResolver,
)
from oarepo_requests.resources.draft.resource import DraftRecordRequestsResource
from oarepo_requests.resources.draft.types.resource import DraftRequestTypesResource
from oarepo_requests.services.draft.service import DraftRecordRequestsService
from oarepo_requests.services.draft.types.service import DraftRecordRequestTypesService

from datasets.files.api import DatasetsFile, DatasetsFileDraft
from datasets.files.requests.resolvers import DatasetsFileDraftResolver
from datasets.records.api import DatasetsDraft, DatasetsRecord
from datasets.records.requests.resolvers import DatasetsDraftResolver, DatasetsResolver
from datasets.resources.files.config import (
    DatasetsFileDraftResourceConfig,
    DatasetsFileResourceConfig,
)
from datasets.resources.files.resource import (
    DatasetsFileDraftResource,
    DatasetsFileResource,
)
from datasets.resources.records.config import DatasetsResourceConfig
from datasets.resources.records.resource import DatasetsResource
from datasets.services.files.config import (
    DatasetsFileDraftServiceConfig,
    DatasetsFileServiceConfig,
)
from datasets.services.files.service import (
    DatasetsFileDraftService,
    DatasetsFileService,
)
from datasets.services.records.config import DatasetsServiceConfig
from datasets.services.records.service import DatasetsService

DATASETS_RECORD_RESOURCE_CONFIG = DatasetsResourceConfig


DATASETS_RECORD_RESOURCE_CLASS = DatasetsResource


DATASETS_RECORD_SERVICE_CONFIG = DatasetsServiceConfig


DATASETS_RECORD_SERVICE_CLASS = DatasetsService


OAREPO_PRIMARY_RECORD_SERVICE = {
    DatasetsRecord: "datasets",
    DatasetsDraft: "datasets",
    DatasetsFile: "datasets_file",
    DatasetsFileDraft: "datasets_file_draft",
}


DATASETS_REQUESTS_RESOURCE_CLASS = DraftRecordRequestsResource


DATASETS_REQUESTS_SERVICE_CLASS = DraftRecordRequestsService


DATASETS_ENTITY_RESOLVERS = [
    DatasetsResolver(
        record_cls=DatasetsRecord, service_id="datasets", type_key="datasets"
    ),
    DatasetsDraftResolver(
        record_cls=DatasetsDraft, service_id="datasets", type_key="datasets_draft"
    ),
    DatasetsFileDraftResolver(
        record_cls=DatasetsFileDraft,
        service_id="datasets_file_draft",
        type_key="datasets_file_draft",
    ),
]


ENTITY_REFERENCE_UI_RESOLVERS = {
    "datasets": RecordEntityReferenceUIResolver("datasets"),
    "datasets_draft": RecordEntityDraftReferenceUIResolver("datasets_draft"),
}
REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = []
NOTIFICATIONS_ENTITY_RESOLVERS = [
    ServiceResultResolver(service_id="datasets", type_key="datasets"),
    DraftServiceResultResolver(
        service_id="datasets",
        type_key="datasets_draft",
        proxy_cls=RDMRecordServiceResultProxy,
    ),
]


DATASETS_REQUEST_TYPES_RESOURCE_CLASS = DraftRequestTypesResource


DATASETS_REQUEST_TYPES_SERVICE_CLASS = DraftRecordRequestTypesService


DATASETS_FILES_RESOURCE_CONFIG = DatasetsFileResourceConfig


DATASETS_FILES_RESOURCE_CLASS = DatasetsFileResource


DATASETS_FILES_SERVICE_CONFIG = DatasetsFileServiceConfig


DATASETS_FILES_SERVICE_CLASS = DatasetsFileService


DATASETS_DRAFT_FILES_RESOURCE_CONFIG = DatasetsFileDraftResourceConfig


DATASETS_DRAFT_FILES_RESOURCE_CLASS = DatasetsFileDraftResource


DATASETS_DRAFT_FILES_SERVICE_CONFIG = DatasetsFileDraftServiceConfig


DATASETS_DRAFT_FILES_SERVICE_CLASS = DatasetsFileDraftService
