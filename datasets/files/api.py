from datasets.files.models import DatasetsFileDraftMetadata, DatasetsFileMetadata
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import IndexField


class DatasetsFile(FileRecord):

    model_cls = DatasetsFileMetadata

    index = IndexField(
        "datasets_file-datasets_file-1.0.0",
    )
    record_cls = None  # is defined inside the parent record


class DatasetsFileDraft(FileRecord):

    model_cls = DatasetsFileDraftMetadata

    index = IndexField(
        "datasets_file_draft-datasets_file_draft-1.0.0",
    )
    record_cls = None  # is defined inside the parent record
