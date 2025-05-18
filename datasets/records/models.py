from invenio_communities.records.records.models import CommunityRelationMixin
from invenio_db import db
from invenio_drafts_resources.records import (
    DraftMetadataBase,
    ParentRecordMixin,
    ParentRecordStateMixin,
)
from invenio_files_rest.models import Bucket
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_records.models import RecordMetadataBase
from oarepo_workflows.records.models import RecordWorkflowParentModelMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils.types import ChoiceType, UUIDType


class DatasetsParentMetadata(
    RecordWorkflowParentModelMixin, db.Model, RecordMetadataBase
):

    __tablename__ = "datasets_parent_record_metadata"


class DatasetsMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Model for DatasetsRecord metadata."""

    __tablename__ = "datasets_metadata"

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}

    __parent_record_model__ = DatasetsParentMetadata

    deletion_status = db.Column(
        ChoiceType(RecordDeletionStatusEnum, impl=db.String(1)),
        nullable=False,
        default=RecordDeletionStatusEnum.PUBLISHED.value,
    )

    media_bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    media_bucket = db.relationship(Bucket, foreign_keys=[media_bucket_id])
    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])


class DatasetsDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):
    """Model for DatasetsDraft metadata."""

    __tablename__ = "datasets_draft_metadata"

    __parent_record_model__ = DatasetsParentMetadata

    deletion_status = db.Column(
        ChoiceType(RecordDeletionStatusEnum, impl=db.String(1)),
        nullable=False,
        default=RecordDeletionStatusEnum.PUBLISHED.value,
    )

    media_bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    media_bucket = db.relationship(Bucket, foreign_keys=[media_bucket_id])
    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])


class DatasetsCommunitiesMetadata(db.Model, CommunityRelationMixin):
    __tablename__ = "datasets_communities_metadata"
    __record_model__ = DatasetsParentMetadata


class DatasetsParentState(db.Model, ParentRecordStateMixin):
    table_name = "datasets_parent_state_metadata"

    __parent_record_model__ = DatasetsParentMetadata
    __record_model__ = DatasetsMetadata
    __draft_model__ = DatasetsDraftMetadata
