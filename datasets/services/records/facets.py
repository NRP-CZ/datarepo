"""Facet definitions."""

from invenio_records_resources.services.records.facets import TermsFacet
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_runtime.services.facets import MultilingualFacet
from oarepo_runtime.services.facets.date import DateTimeFacet
from oarepo_runtime.services.facets.nested_facet import NestedLabeledFacet
from oarepo_vocabularies.services.facets import VocabularyFacet

access_embargo_active = TermsFacet(
    field="access.embargo.active", label=_("access/embargo/active.label")
)

access_embargo_until = DateTimeFacet(
    field="access.embargo.until", label=_("access/embargo/until.label")
)

access_files = TermsFacet(field="access.files", label=_("access/files.label"))

access_record = TermsFacet(field="access.record", label=_("access/record.label"))

access_status = TermsFacet(field="access.status", label=_("access/status.label"))

metadata_alternate_identifiers_identifier = TermsFacet(
    field="metadata.alternate_identifiers.identifier",
    label=_("metadata/alternate_identifiers/identifier.label"),
)

metadata_alternate_identifiers_scheme = TermsFacet(
    field="metadata.alternate_identifiers.scheme",
    label=_("metadata/alternate_identifiers/scheme.label"),
)

metadata_alternate_titles_title_cs = TermsFacet(
    field="metadata.alternate_titles.title_cs.keyword",
    label=_("metadata/alternate_titles/title.label"),
)

metadata_alternate_titles_title_en = TermsFacet(
    field="metadata.alternate_titles.title_en.keyword",
    label=_("metadata/alternate_titles/title.label"),
)

metadata_alternate_titles_title = MultilingualFacet(
    lang_facets={
        "cs": metadata_alternate_titles_title_cs,
        "en": metadata_alternate_titles_title_en,
    },
    label=_("metadata/alternate_titles/title.label"),
)

metadata_alternate_titles_title_lang = NestedLabeledFacet(
    path="metadata.alternate_titles.title",
    nested_facet=TermsFacet(
        field="metadata.alternate_titles.title.lang",
        label=_("metadata/alternate_titles/title/lang.label"),
    ),
)

metadata_alternate_titles_titleType = VocabularyFacet(
    field="metadata.alternate_titles.titleType",
    label=_("metadata/alternate_titles/titleType.label"),
    vocabulary="title-types",
)

metadata_contributors_affiliations = VocabularyFacet(
    field="metadata.contributors.affiliations",
    label=_("metadata/contributors/affiliations.label"),
    vocabulary="affiliations",
)

metadata_contributors_person_or_org_family_name = TermsFacet(
    field="metadata.contributors.person_or_org.family_name",
    label=_("metadata/contributors/person_or_org/family_name.label"),
)

metadata_contributors_person_or_org_given_name = TermsFacet(
    field="metadata.contributors.person_or_org.given_name",
    label=_("metadata/contributors/person_or_org/given_name.label"),
)

metadata_contributors_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.contributors.person_or_org.identifiers.identifier",
    label=_("metadata/contributors/person_or_org/identifiers/identifier.label"),
)

metadata_contributors_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.contributors.person_or_org.identifiers.scheme",
    label=_("metadata/contributors/person_or_org/identifiers/scheme.label"),
)

metadata_contributors_person_or_org_name = TermsFacet(
    field="metadata.contributors.person_or_org.name",
    label=_("metadata/contributors/person_or_org/name.label"),
)

metadata_contributors_person_or_org_type = TermsFacet(
    field="metadata.contributors.person_or_org.type",
    label=_("metadata/contributors/person_or_org/type.label"),
)

metadata_contributors_role = VocabularyFacet(
    field="metadata.contributors.role",
    label=_("metadata/contributors/role.label"),
    vocabulary="contributor-types",
)

metadata_creators_affiliations = VocabularyFacet(
    field="metadata.creators.affiliations",
    label=_("metadata/creators/affiliations.label"),
    vocabulary="affiliations",
)

metadata_creators_person_or_org_family_name = TermsFacet(
    field="metadata.creators.person_or_org.family_name",
    label=_("metadata/creators/person_or_org/family_name.label"),
)

metadata_creators_person_or_org_given_name = TermsFacet(
    field="metadata.creators.person_or_org.given_name",
    label=_("metadata/creators/person_or_org/given_name.label"),
)

metadata_creators_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.creators.person_or_org.identifiers.identifier",
    label=_("metadata/creators/person_or_org/identifiers/identifier.label"),
)

metadata_creators_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.creators.person_or_org.identifiers.scheme",
    label=_("metadata/creators/person_or_org/identifiers/scheme.label"),
)

metadata_creators_person_or_org_name = TermsFacet(
    field="metadata.creators.person_or_org.name",
    label=_("metadata/creators/person_or_org/name.label"),
)

metadata_creators_person_or_org_type = TermsFacet(
    field="metadata.creators.person_or_org.type",
    label=_("metadata/creators/person_or_org/type.label"),
)

metadata_creators_role = VocabularyFacet(
    field="metadata.creators.role",
    label=_("metadata/creators/role.label"),
    vocabulary="contributor-types",
)

metadata_date_issued = DateTimeFacet(
    field="metadata.date_issued", label=_("metadata/date_issued.label")
)

metadata_descriptions_cs = TermsFacet(
    field="metadata.descriptions_cs.keyword", label=_("metadata/descriptions.label")
)

metadata_descriptions_en = TermsFacet(
    field="metadata.descriptions_en.keyword", label=_("metadata/descriptions.label")
)

metadata_descriptions = MultilingualFacet(
    lang_facets={
        "cs": metadata_descriptions_cs,
        "en": metadata_descriptions_en,
    },
    label=_("metadata/descriptions.label"),
)

metadata_descriptions_lang = NestedLabeledFacet(
    path="metadata.descriptions",
    nested_facet=TermsFacet(
        field="metadata.descriptions.lang", label=_("metadata/descriptions/lang.label")
    ),
)

metadata_funding_references_award = VocabularyFacet(
    field="metadata.funding_references.award",
    label=_("metadata/funding_references/award.label"),
    vocabulary="awards",
)

metadata_funding_references_funder = VocabularyFacet(
    field="metadata.funding_references.funder",
    label=_("metadata/funding_references/funder.label"),
    vocabulary="funders",
)

metadata_other_languages = VocabularyFacet(
    field="metadata.other_languages",
    label=_("metadata/other_languages.label"),
    vocabulary="languages",
)

metadata_primary_language = VocabularyFacet(
    field="metadata.primary_language",
    label=_("metadata/primary_language.label"),
    vocabulary="languages",
)

metadata_publisher_affiliations = VocabularyFacet(
    field="metadata.publisher.affiliations",
    label=_("metadata/publisher/affiliations.label"),
    vocabulary="affiliations",
)

metadata_publisher_person_or_org_family_name = TermsFacet(
    field="metadata.publisher.person_or_org.family_name",
    label=_("metadata/publisher/person_or_org/family_name.label"),
)

metadata_publisher_person_or_org_given_name = TermsFacet(
    field="metadata.publisher.person_or_org.given_name",
    label=_("metadata/publisher/person_or_org/given_name.label"),
)

metadata_publisher_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.publisher.person_or_org.identifiers.identifier",
    label=_("metadata/publisher/person_or_org/identifiers/identifier.label"),
)

metadata_publisher_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.publisher.person_or_org.identifiers.scheme",
    label=_("metadata/publisher/person_or_org/identifiers/scheme.label"),
)

metadata_publisher_person_or_org_name = TermsFacet(
    field="metadata.publisher.person_or_org.name",
    label=_("metadata/publisher/person_or_org/name.label"),
)

metadata_publisher_person_or_org_type = TermsFacet(
    field="metadata.publisher.person_or_org.type",
    label=_("metadata/publisher/person_or_org/type.label"),
)

metadata_publisher_role = VocabularyFacet(
    field="metadata.publisher.role",
    label=_("metadata/publisher/role.label"),
    vocabulary="contributor-types",
)

metadata_related_resources_contributors_affiliations = VocabularyFacet(
    field="metadata.related_resources.contributors.affiliations",
    label=_("metadata/related_resources/contributors/affiliations.label"),
    vocabulary="affiliations",
)

metadata_related_resources_contributors_person_or_org_family_name = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.family_name",
    label=_("metadata/related_resources/contributors/person_or_org/family_name.label"),
)

metadata_related_resources_contributors_person_or_org_given_name = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.given_name",
    label=_("metadata/related_resources/contributors/person_or_org/given_name.label"),
)

metadata_related_resources_contributors_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.identifiers.identifier",
    label=_(
        "metadata/related_resources/contributors/person_or_org/identifiers/identifier.label"
    ),
)

metadata_related_resources_contributors_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.identifiers.scheme",
    label=_(
        "metadata/related_resources/contributors/person_or_org/identifiers/scheme.label"
    ),
)

metadata_related_resources_contributors_person_or_org_name = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.name",
    label=_("metadata/related_resources/contributors/person_or_org/name.label"),
)

metadata_related_resources_contributors_person_or_org_type = TermsFacet(
    field="metadata.related_resources.contributors.person_or_org.type",
    label=_("metadata/related_resources/contributors/person_or_org/type.label"),
)

metadata_related_resources_contributors_role = VocabularyFacet(
    field="metadata.related_resources.contributors.role",
    label=_("metadata/related_resources/contributors/role.label"),
    vocabulary="contributor-types",
)

metadata_related_resources_creators_affiliations = VocabularyFacet(
    field="metadata.related_resources.creators.affiliations",
    label=_("metadata/related_resources/creators/affiliations.label"),
    vocabulary="affiliations",
)

metadata_related_resources_creators_person_or_org_family_name = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.family_name",
    label=_("metadata/related_resources/creators/person_or_org/family_name.label"),
)

metadata_related_resources_creators_person_or_org_given_name = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.given_name",
    label=_("metadata/related_resources/creators/person_or_org/given_name.label"),
)

metadata_related_resources_creators_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.identifiers.identifier",
    label=_(
        "metadata/related_resources/creators/person_or_org/identifiers/identifier.label"
    ),
)

metadata_related_resources_creators_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.identifiers.scheme",
    label=_(
        "metadata/related_resources/creators/person_or_org/identifiers/scheme.label"
    ),
)

metadata_related_resources_creators_person_or_org_name = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.name",
    label=_("metadata/related_resources/creators/person_or_org/name.label"),
)

metadata_related_resources_creators_person_or_org_type = TermsFacet(
    field="metadata.related_resources.creators.person_or_org.type",
    label=_("metadata/related_resources/creators/person_or_org/type.label"),
)

metadata_related_resources_creators_role = VocabularyFacet(
    field="metadata.related_resources.creators.role",
    label=_("metadata/related_resources/creators/role.label"),
    vocabulary="contributor-types",
)

metadata_related_resources_identifiers_identifier = TermsFacet(
    field="metadata.related_resources.identifiers.identifier",
    label=_("metadata/related_resources/identifiers/identifier.label"),
)

metadata_related_resources_identifiers_scheme = TermsFacet(
    field="metadata.related_resources.identifiers.scheme",
    label=_("metadata/related_resources/identifiers/scheme.label"),
)

metadata_related_resources_publisher_affiliations = VocabularyFacet(
    field="metadata.related_resources.publisher.affiliations",
    label=_("metadata/related_resources/publisher/affiliations.label"),
    vocabulary="affiliations",
)

metadata_related_resources_publisher_person_or_org_family_name = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.family_name",
    label=_("metadata/related_resources/publisher/person_or_org/family_name.label"),
)

metadata_related_resources_publisher_person_or_org_given_name = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.given_name",
    label=_("metadata/related_resources/publisher/person_or_org/given_name.label"),
)

metadata_related_resources_publisher_person_or_org_identifiers_identifier = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.identifiers.identifier",
    label=_(
        "metadata/related_resources/publisher/person_or_org/identifiers/identifier.label"
    ),
)

metadata_related_resources_publisher_person_or_org_identifiers_scheme = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.identifiers.scheme",
    label=_(
        "metadata/related_resources/publisher/person_or_org/identifiers/scheme.label"
    ),
)

metadata_related_resources_publisher_person_or_org_name = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.name",
    label=_("metadata/related_resources/publisher/person_or_org/name.label"),
)

metadata_related_resources_publisher_person_or_org_type = TermsFacet(
    field="metadata.related_resources.publisher.person_or_org.type",
    label=_("metadata/related_resources/publisher/person_or_org/type.label"),
)

metadata_related_resources_publisher_role = VocabularyFacet(
    field="metadata.related_resources.publisher.role",
    label=_("metadata/related_resources/publisher/role.label"),
    vocabulary="contributor-types",
)

metadata_related_resources_relation_type = VocabularyFacet(
    field="metadata.related_resources.relation_type",
    label=_("metadata/related_resources/relation_type.label"),
    vocabulary="relation-types",
)

metadata_related_resources_resource_url = TermsFacet(
    field="metadata.related_resources.resource_url",
    label=_("metadata/related_resources/resource_url.label"),
)

metadata_related_resources_time_references_date = DateTimeFacet(
    field="metadata.related_resources.time_references.date",
    label=_("metadata/related_resources/time_references/date.label"),
)

metadata_related_resources_time_references_date_information = TermsFacet(
    field="metadata.related_resources.time_references.date_information",
    label=_("metadata/related_resources/time_references/date_information.label"),
)

metadata_related_resources_time_references_date_type = VocabularyFacet(
    field="metadata.related_resources.time_references.date_type",
    label=_("metadata/related_resources/time_references/date_type.label"),
    vocabulary="time-reference-types",
)

metadata_related_resources_type = VocabularyFacet(
    field="metadata.related_resources.type",
    label=_("metadata/related_resources/type.label"),
    vocabulary="resource-types",
)

metadata_resource_type = VocabularyFacet(
    field="metadata.resource_type",
    label=_("metadata/resource_type.label"),
    vocabulary="resource-types",
)

metadata_subjects_classificationCode = TermsFacet(
    field="metadata.subjects.classificationCode",
    label=_("metadata/subjects/classificationCode.label"),
)

metadata_subjects_iri = TermsFacet(
    field="metadata.subjects.iri", label=_("metadata/subjects/iri.label")
)

metadata_subjects_subject_cs = TermsFacet(
    field="metadata.subjects.subject_cs.keyword",
    label=_("metadata/subjects/subject.label"),
)

metadata_subjects_subject_en = TermsFacet(
    field="metadata.subjects.subject_en.keyword",
    label=_("metadata/subjects/subject.label"),
)

metadata_subjects_subject = MultilingualFacet(
    lang_facets={
        "cs": metadata_subjects_subject_cs,
        "en": metadata_subjects_subject_en,
    },
    label=_("metadata/subjects/subject.label"),
)

metadata_subjects_subject_lang = NestedLabeledFacet(
    path="metadata.subjects.subject",
    nested_facet=TermsFacet(
        field="metadata.subjects.subject.lang",
        label=_("metadata/subjects/subject/lang.label"),
    ),
)

metadata_subjects_subjectScheme = VocabularyFacet(
    field="metadata.subjects.subjectScheme",
    label=_("metadata/subjects/subjectScheme.label"),
    vocabulary="subject-schemes",
)

metadata_terms_of_use_access_rights = VocabularyFacet(
    field="metadata.terms_of_use.access_rights",
    label=_("metadata/terms_of_use/access_rights.label"),
    vocabulary="access-rights",
)

metadata_terms_of_use_descriptions_cs = TermsFacet(
    field="metadata.terms_of_use.descriptions_cs.keyword",
    label=_("metadata/terms_of_use/descriptions.label"),
)

metadata_terms_of_use_descriptions_en = TermsFacet(
    field="metadata.terms_of_use.descriptions_en.keyword",
    label=_("metadata/terms_of_use/descriptions.label"),
)

metadata_terms_of_use_descriptions = MultilingualFacet(
    lang_facets={
        "cs": metadata_terms_of_use_descriptions_cs,
        "en": metadata_terms_of_use_descriptions_en,
    },
    label=_("metadata/terms_of_use/descriptions.label"),
)

metadata_terms_of_use_descriptions_lang = NestedLabeledFacet(
    path="metadata.terms_of_use.descriptions",
    nested_facet=TermsFacet(
        field="metadata.terms_of_use.descriptions.lang",
        label=_("metadata/terms_of_use/descriptions/lang.label"),
    ),
)

metadata_terms_of_use_licenses = VocabularyFacet(
    field="metadata.terms_of_use.licenses",
    label=_("metadata/terms_of_use/licenses.label"),
    vocabulary="licenses",
)

metadata_time_references_date = DateTimeFacet(
    field="metadata.time_references.date",
    label=_("metadata/time_references/date.label"),
)

metadata_time_references_date_information = TermsFacet(
    field="metadata.time_references.date_information",
    label=_("metadata/time_references/date_information.label"),
)

metadata_time_references_date_type = VocabularyFacet(
    field="metadata.time_references.date_type",
    label=_("metadata/time_references/date_type.label"),
    vocabulary="time-reference-types",
)

metadata_version = TermsFacet(
    field="metadata.version", label=_("metadata/version.label")
)

state = TermsFacet(field="state", label=_("state.label"))

state_timestamp = DateTimeFacet(
    field="state_timestamp", label=_("state_timestamp.label")
)


record_status = TermsFacet(field="record_status", label=_("record_status"))

has_draft = TermsFacet(field="has_draft", label=_("has_draft"))

expires_at = DateTimeFacet(field="expires_at", label=_("expires_at.label"))

fork_version_id = TermsFacet(field="fork_version_id", label=_("fork_version_id.label"))
