import marshmallow as ma
from marshmallow import Schema
from marshmallow import fields as ma_fields
from marshmallow.fields import String
from oarepo_requests.services.ui_schema import UIRequestsSerializationMixin
from oarepo_runtime.services.schema.i18n_ui import I18nStrUIField
from oarepo_runtime.services.schema.marshmallow import DictOnlySchema
from oarepo_runtime.services.schema.rdm_ui import (
    RDMCreatorsUISchema,
    RDMFundersUISchema,
    RDMIdentifierWithSchemaUISchema,
)
from oarepo_runtime.services.schema.ui import (
    InvenioRDMUISchema,
    LocalizedDate,
    LocalizedDateTime,
)
from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField


class DatasetsUISchema(UIRequestsSerializationMixin, InvenioRDMUISchema):
    class Meta:
        unknown = ma.RAISE

    deletion_status = ma_fields.String()

    is_deleted = ma_fields.Boolean()

    is_published = ma_fields.Boolean()

    metadata = ma_fields.Nested(lambda: DatasetsMetadataUISchema())

    state = ma_fields.String(dump_only=True)

    state_timestamp = LocalizedDateTime(dump_only=True)

    version_id = ma_fields.Integer()


class DatasetsMetadataUISchema(Schema):
    class Meta:
        unknown = ma.RAISE

    alternate_identifiers = ma_fields.List(
        ma_fields.Nested(lambda: RDMIdentifierWithSchemaUISchema())
    )

    alternate_titles = ma_fields.List(
        ma_fields.Nested(lambda: AlternateTitlesItemUISchema())
    )

    contributors = ma_fields.List(ma_fields.Nested(lambda: RDMCreatorsUISchema()))

    creators = ma_fields.List(ma_fields.Nested(lambda: RDMCreatorsUISchema()))

    date_issued = LocalizedDate(required=True)

    descriptions = ma_fields.List(I18nStrUIField())

    funding_references = ma_fields.List(ma_fields.Nested(lambda: RDMFundersUISchema()))

    other_languages = ma_fields.List(ma_fields.Nested(lambda: TitleTypeUISchema()))

    primary_language = ma_fields.Nested(lambda: TitleTypeUISchema())

    publisher = ma_fields.Nested(lambda: RDMCreatorsUISchema())

    related_resources = ma_fields.List(
        ma_fields.Nested(lambda: RelatedResourcesItemUISchema())
    )

    resource_type = ma_fields.Nested(lambda: TitleTypeUISchema(), required=True)

    subjects = ma_fields.List(ma_fields.Nested(lambda: MetadataSubjectsItemUISchema()))

    terms_of_use = ma_fields.Nested(lambda: TermsOfUseUISchema())

    time_references = ma_fields.List(
        ma_fields.Nested(lambda: TimeReferencesItemUISchema())
    )

    title = ma_fields.String(required=True)

    version = ma_fields.String()


class RelatedResourcesItemUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    contributors = ma_fields.List(ma_fields.Nested(lambda: RDMCreatorsUISchema()))

    creators = ma_fields.List(ma_fields.Nested(lambda: RDMCreatorsUISchema()))

    identifiers = ma_fields.List(
        ma_fields.Nested(lambda: RDMIdentifierWithSchemaUISchema())
    )

    publisher = ma_fields.Nested(lambda: RDMCreatorsUISchema())

    relation_type = ma_fields.Nested(lambda: TitleTypeUISchema())

    resource_url = ma_fields.String()

    time_references = ma_fields.List(
        ma_fields.Nested(lambda: TimeReferencesItemUISchema())
    )

    title = ma_fields.String()

    type = ma_fields.Nested(lambda: TitleTypeUISchema())


class AlternateTitlesItemUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    title = I18nStrUIField(required=True)

    titleType = ma_fields.Nested(lambda: TitleTypeUISchema(), required=True)


class MetadataSubjectsItemUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    classificationCode = ma_fields.String()

    iri = ma_fields.String()

    subject = I18nStrUIField()

    subjectScheme = ma_fields.Nested(lambda: TitleTypeUISchema())


class TermsOfUseUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    access_rights = ma_fields.Nested(lambda: TitleTypeUISchema())

    descriptions = ma_fields.List(I18nStrUIField())

    licenses = ma_fields.List(ma_fields.Nested(lambda: TitleTypeUISchema()))


class TimeReferencesItemUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.RAISE

    date = LocalizedDate()

    date_information = ma_fields.String()

    date_type = ma_fields.Nested(lambda: TitleTypeUISchema())


class TitleTypeUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.INCLUDE

    _id = String(data_key="id", attribute="id")

    _version = String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()
