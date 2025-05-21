import marshmallow as ma
from invenio_rdm_records.services.schemas.access import AccessSchema
from invenio_rdm_records.services.schemas.metadata import CreatorSchema
from invenio_rdm_records.services.schemas.pids import PIDSchema
from invenio_rdm_records.services.schemas.record import validate_scheme
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import Schema
from marshmallow import fields as ma_fields
from marshmallow.fields import Dict, Nested, String
from marshmallow.utils import get_value
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.fields.nestedattr import NestedAttribute
from oarepo_communities.schemas.parent import CommunitiesParentSchema
from oarepo_runtime.services.schema.i18n import I18nStrField, MultilingualField
from oarepo_runtime.services.schema.marshmallow import (
    DictOnlySchema,
    RDMBaseRecordSchema,
)
from oarepo_runtime.services.schema.rdm import (
    FundingSchema,
    RecordIdentifierField,
    RelatedRecordIdentifierField,
)
from oarepo_runtime.services.schema.validation import validate_date, validate_datetime
from oarepo_workflows.services.records.schema import RDMWorkflowParentSchema


class GeneratedParentSchema(RDMWorkflowParentSchema):
    """"""

    owners = ma.fields.List(ma.fields.Dict(), load_only=True)

    communities = ma_fields.Nested(CommunitiesParentSchema)


class DatasetsSchema(RDMBaseRecordSchema):
    class Meta:
        unknown = ma.RAISE

    access = NestedAttribute(lambda: AccessSchema())

    metadata = ma_fields.Nested(lambda: DatasetsMetadataSchema())

    pids = Dict(
        keys=SanitizedUnicode(validate=validate_scheme),
        values=Nested(PIDSchema),
    )

    state = ma_fields.String(dump_only=True)

    state_timestamp = ma_fields.String(dump_only=True, validate=[validate_datetime])
    parent = ma.fields.Nested(GeneratedParentSchema)
    files = ma.fields.Nested(
        lambda: FilesOptionsSchema(), load_default={"enabled": True}
    )

    # todo this needs to be generated for [default preview] to work
    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        if attr == "files":
            return getattr(obj, attr, default)
        else:
            return get_value(obj, attr, default)


class DatasetsMetadataSchema(Schema):
    class Meta:
        unknown = ma.RAISE

    alternate_identifiers = RecordIdentifierField()

    alternate_titles = ma_fields.List(
        ma_fields.Nested(lambda: AlternateTitlesItemSchema())
    )

    contributors = ma_fields.List(ma_fields.Nested(lambda: CreatorSchema()))

    creators = ma_fields.List(ma_fields.Nested(lambda: CreatorSchema()))

    date_issued = ma_fields.String(required=True, validate=[validate_date("%Y-%m-%d")])

    descriptions = ma_fields.List(I18nStrField())

    funding_references = ma_fields.List(ma_fields.Nested(lambda: FundingSchema()))

    other_languages = ma_fields.List(ma_fields.Nested(lambda: TitleTypeSchema()))

    primary_language = ma_fields.Nested(lambda: TitleTypeSchema())

    publisher = ma_fields.Nested(lambda: CreatorSchema())

    related_resources = ma_fields.List(
        ma_fields.Nested(lambda: RelatedResourcesItemSchema())
    )

    resource_type = ma_fields.Nested(lambda: TitleTypeSchema(), required=True)

    subjects = ma_fields.List(ma_fields.Nested(lambda: MetadataSubjectsItemSchema()))

    terms_of_use = ma_fields.Nested(lambda: TermsOfUseSchema())

    time_references = ma_fields.List(
        ma_fields.Nested(lambda: TimeReferencesItemSchema())
    )

    title = ma_fields.String(required=True)

    version = ma_fields.String()


class RelatedResourcesItemSchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    contributors = ma_fields.List(ma_fields.Nested(lambda: CreatorSchema()))

    creators = ma_fields.List(ma_fields.Nested(lambda: CreatorSchema()))

    identifiers = RelatedRecordIdentifierField()

    publisher = ma_fields.Nested(lambda: CreatorSchema())

    relation_type = ma_fields.Nested(lambda: TitleTypeSchema())

    resource_url = ma_fields.String()

    time_references = ma_fields.List(
        ma_fields.Nested(lambda: TimeReferencesItemSchema())
    )

    title = ma_fields.String()

    type = ma_fields.Nested(lambda: TitleTypeSchema())


class AlternateTitlesItemSchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    title = I18nStrField(required=True)

    titleType = ma_fields.Nested(lambda: TitleTypeSchema(), required=True)


class MetadataSubjectsItemSchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    classificationCode = ma_fields.String()

    iri = ma_fields.String()

    subject = MultilingualField(I18nStrField(), required=True)

    subjectScheme = ma_fields.Nested(lambda: TitleTypeSchema())


class TermsOfUseSchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    access_rights = ma_fields.Nested(lambda: TitleTypeSchema())

    descriptions = ma_fields.List(I18nStrField())

    licenses = ma_fields.List(ma_fields.Nested(lambda: TitleTypeSchema()))


class TimeReferencesItemSchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    date = ma_fields.String(validate=[validate_date("%Y-%m-%d")])

    date_information = ma_fields.String()

    date_type = ma_fields.Nested(lambda: TitleTypeSchema())


class TitleTypeSchema(DictOnlySchema):
    class Meta:
        unknown = ma.INCLUDE

    _id = String(data_key="id", attribute="id")

    _version = String(data_key="@v", attribute="@v")

    title = i18n_strings


class FilesOptionsSchema(ma.Schema):
    """Basic files options schema class."""

    enabled = ma.fields.Bool(missing=True)
    # allow unsetting
    default_preview = SanitizedUnicode(allow_none=True)

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        value = getattr(obj, attr, default)

        if attr == "default_preview" and not value:
            return default

        return value
