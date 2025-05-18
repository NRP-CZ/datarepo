import marshmallow as ma
from marshmallow import Schema
from marshmallow import fields as ma_fields
from marshmallow.fields import String
from oarepo_requests.services.ui_schema import UIRequestsSerializationMixin
from oarepo_runtime.services.schema.marshmallow import DictOnlySchema
from oarepo_runtime.services.schema.ui import InvenioRDMUISchema, LocalizedDateTime
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

    languages = ma_fields.List(ma_fields.Nested(lambda: LanguagesItemUISchema()))

    title = ma_fields.String()

    version = ma_fields.String()


class LanguagesItemUISchema(DictOnlySchema):
    class Meta:
        unknown = ma.INCLUDE

    _id = String(data_key="id", attribute="id")

    _version = String(data_key="@v", attribute="@v")

    title = VocabularyI18nStrUIField()
