from invenio_communities.records.records.systemfields import CommunitiesField
from invenio_drafts_resources.records.api import DraftRecordIdProviderV2
from invenio_drafts_resources.services.records.components.media_files import (
    MediaFilesAttrConfig,
)
from invenio_rdm_records.records.api import (
    RDMDraft,
    RDMMediaFileDraft,
    RDMMediaFileRecord,
    RDMParent,
    RDMRecord,
)
from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.systemfields import FilesField, IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from oarepo_communities.records.systemfields.communities import (
    OARepoCommunitiesFieldContext,
)
from oarepo_runtime.records.pid_providers import UniversalPIDMixin
from oarepo_runtime.records.relations import (
    PIDRelation,
    RelationsField,
    UnstrictPIDRelation,
)
from oarepo_runtime.records.systemfields.has_draftcheck import HasDraftCheckField
from oarepo_runtime.records.systemfields.record_status import RecordStatusSystemField
from oarepo_vocabularies.records.api import Vocabulary
from oarepo_workflows.records.systemfields.state import (
    RecordStateField,
    RecordStateTimestampField,
)
from oarepo_workflows.records.systemfields.workflow import WorkflowField

from datasets.files.api import DatasetsFile, DatasetsFileDraft
from datasets.records.dumpers.dumper import DatasetsDraftDumper, DatasetsDumper
from datasets.records.models import (
    DatasetsCommunitiesMetadata,
    DatasetsDraftMetadata,
    DatasetsMetadata,
    DatasetsParentMetadata,
    DatasetsParentState,
)


class DatasetsParentRecord(RDMParent):
    model_cls = DatasetsParentMetadata

    workflow = WorkflowField()

    communities = CommunitiesField(
        DatasetsCommunitiesMetadata, context_cls=OARepoCommunitiesFieldContext
    )


class DatasetsIdProvider(UniversalPIDMixin, DraftRecordIdProviderV2):
    pid_type = "dtsts"


class DatasetsRecord(RDMRecord):

    model_cls = DatasetsMetadata

    schema = ConstantField("$schema", "local://datasets-1.0.0.json")

    index = IndexField(
        "datasets-datasets-1.0.0",
    )

    pid = PIDField(
        provider=DatasetsIdProvider, context_cls=PIDFieldContext, create=True
    )

    dumper = DatasetsDumper()

    state = RecordStateField(initial="published")

    state_timestamp = RecordStateTimestampField()

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=RDMMediaFileRecord,
        create=False,
        delete=False,
    )

    relations = RelationsField(
        titleType=PIDRelation(
            "metadata.alternate_titles.titleType",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("title-types"),
        ),
        affiliations=UnstrictPIDRelation(
            "metadata.contributors.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        role=PIDRelation(
            "metadata.contributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        creators_affiliations=UnstrictPIDRelation(
            "metadata.creators.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        creators_role=PIDRelation(
            "metadata.creators.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        award=UnstrictPIDRelation(
            "metadata.funding_references.award",
            keys=[
                "title",
                "id",
                "number",
                "program",
                "acronym",
                "identifiers",
                "subjects",
                "organizations",
                "@v",
            ],
            pid_field=Award.pid,
        ),
        funder=UnstrictPIDRelation(
            "metadata.funding_references.funder",
            keys=["id", "@v", "name", "title"],
            pid_field=Funder.pid,
        ),
        other_languages=PIDRelation(
            "metadata.other_languages",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        primary_language=PIDRelation(
            "metadata.primary_language",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        publisher_affiliations=UnstrictPIDRelation(
            "metadata.publisher.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        publisher_role=PIDRelation(
            "metadata.publisher.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        contributors_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.contributors.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        contributors_role=PIDRelation(
            "metadata.related_resources.contributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        related_resources_creators_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.creators.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        related_resources_creators_role=PIDRelation(
            "metadata.related_resources.creators.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        related_resources_publisher_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.publisher.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        related_resources_publisher_role=PIDRelation(
            "metadata.related_resources.publisher.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        relation_type=PIDRelation(
            "metadata.related_resources.relation_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("relation-types"),
        ),
        date_type=PIDRelation(
            "metadata.related_resources.time_references.date_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("time-reference-types"),
        ),
        type=PIDRelation(
            "metadata.related_resources.type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        resource_type=PIDRelation(
            "metadata.resource_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        subjectScheme=PIDRelation(
            "metadata.subjects.subjectScheme",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("subject-schemes"),
        ),
        access_rights=PIDRelation(
            "metadata.terms_of_use.access_rights",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("access-rights"),
        ),
        licenses=PIDRelation(
            "metadata.terms_of_use.licenses",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("licenses"),
        ),
        time_references_date_type=PIDRelation(
            "metadata.time_references.date_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("time-reference-types"),
        ),
    )

    versions_model_cls = DatasetsParentState

    parent_record_cls = DatasetsParentRecord
    record_status = RecordStatusSystemField()
    has_draft = HasDraftCheckField(
        draft_cls=lambda: DatasetsDraft, config_key="HAS_DRAFT_CUSTOM_FIELD"
    )

    files = FilesField(file_cls=DatasetsFile, store=False, create=False, delete=False)

    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)


class RDMRecordMediaFiles(DatasetsRecord):
    """RDM Media file record API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=RDMMediaFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )


class DatasetsDraft(RDMDraft):

    model_cls = DatasetsDraftMetadata

    schema = ConstantField("$schema", "local://datasets-1.0.0.json")

    index = IndexField("datasets-datasets_draft-1.0.0", search_alias="datasets")

    pid = PIDField(
        provider=DatasetsIdProvider,
        context_cls=PIDFieldContext,
        create=True,
        delete=False,
    )

    dumper = DatasetsDraftDumper()

    state = RecordStateField()

    state_timestamp = RecordStateTimestampField()

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=RDMMediaFileDraft,
        create=False,
        delete=False,
    )

    relations = RelationsField(
        titleType=PIDRelation(
            "metadata.alternate_titles.titleType",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("title-types"),
        ),
        affiliations=UnstrictPIDRelation(
            "metadata.contributors.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        role=PIDRelation(
            "metadata.contributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        creators_affiliations=UnstrictPIDRelation(
            "metadata.creators.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        creators_role=PIDRelation(
            "metadata.creators.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        award=UnstrictPIDRelation(
            "metadata.funding_references.award",
            keys=[
                "title",
                "id",
                "number",
                "program",
                "acronym",
                "identifiers",
                "subjects",
                "organizations",
                "@v",
            ],
            pid_field=Award.pid,
        ),
        funder=UnstrictPIDRelation(
            "metadata.funding_references.funder",
            keys=["id", "@v", "name", "title"],
            pid_field=Funder.pid,
        ),
        other_languages=PIDRelation(
            "metadata.other_languages",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        primary_language=PIDRelation(
            "metadata.primary_language",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        publisher_affiliations=UnstrictPIDRelation(
            "metadata.publisher.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        publisher_role=PIDRelation(
            "metadata.publisher.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        contributors_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.contributors.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        contributors_role=PIDRelation(
            "metadata.related_resources.contributors.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        related_resources_creators_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.creators.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        related_resources_creators_role=PIDRelation(
            "metadata.related_resources.creators.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        related_resources_publisher_affiliations=UnstrictPIDRelation(
            "metadata.related_resources.publisher.affiliations",
            keys=["name", "id"],
            pid_field=Affiliation.pid,
        ),
        related_resources_publisher_role=PIDRelation(
            "metadata.related_resources.publisher.role",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributor-types"),
        ),
        relation_type=PIDRelation(
            "metadata.related_resources.relation_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("relation-types"),
        ),
        date_type=PIDRelation(
            "metadata.related_resources.time_references.date_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("time-reference-types"),
        ),
        type=PIDRelation(
            "metadata.related_resources.type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        resource_type=PIDRelation(
            "metadata.resource_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("resource-types"),
        ),
        subjectScheme=PIDRelation(
            "metadata.subjects.subjectScheme",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("subject-schemes"),
        ),
        access_rights=PIDRelation(
            "metadata.terms_of_use.access_rights",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("access-rights"),
        ),
        licenses=PIDRelation(
            "metadata.terms_of_use.licenses",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("licenses"),
        ),
        time_references_date_type=PIDRelation(
            "metadata.time_references.date_type",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("time-reference-types"),
        ),
    )

    versions_model_cls = DatasetsParentState

    parent_record_cls = DatasetsParentRecord
    record_status = RecordStatusSystemField()

    has_draft = HasDraftCheckField(config_key="HAS_DRAFT_CUSTOM_FIELD")

    files = FilesField(file_cls=DatasetsFileDraft, store=False)

    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)


class RDMDraftMediaFiles(DatasetsDraft):
    """RDM Draft media file API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=RDMMediaFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )


RDMMediaFileRecord.record_cls = RDMRecordMediaFiles
RDMMediaFileDraft.record_cls = RDMDraftMediaFiles

DatasetsFile.record_cls = DatasetsRecord

DatasetsFileDraft.record_cls = DatasetsDraft
