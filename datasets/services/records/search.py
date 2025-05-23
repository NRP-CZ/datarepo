from oarepo_runtime.services.search import (
    I18nRDMDraftsSearchOptions,
    I18nRDMSearchOptions,
)

from . import facets


class DatasetsSearchOptions(I18nRDMSearchOptions):
    """DatasetsRecord search options."""

    facet_groups = {}

    facets = {
        **getattr(I18nRDMSearchOptions, "facets", {}),
        "access_embargo_active": facets.access_embargo_active,
        "access_embargo_until": facets.access_embargo_until,
        "access_files": facets.access_files,
        "access_record": facets.access_record,
        "access_status": facets.access_status,
        "metadata_alternate_identifiers_identifier": (
            facets.metadata_alternate_identifiers_identifier
        ),
        "metadata_alternate_identifiers_scheme": (
            facets.metadata_alternate_identifiers_scheme
        ),
        "metadata_alternate_titles_title_cs": facets.metadata_alternate_titles_title_cs,
        "metadata_alternate_titles_title_en": facets.metadata_alternate_titles_title_en,
        "metadata_alternate_titles_title": facets.metadata_alternate_titles_title,
        "metadata_alternate_titles_title_lang": (
            facets.metadata_alternate_titles_title_lang
        ),
        "metadata_alternate_titles_titleType": (
            facets.metadata_alternate_titles_titleType
        ),
        "metadata_contributors_affiliations": facets.metadata_contributors_affiliations,
        "metadata_contributors_person_or_org_family_name": (
            facets.metadata_contributors_person_or_org_family_name
        ),
        "metadata_contributors_person_or_org_given_name": (
            facets.metadata_contributors_person_or_org_given_name
        ),
        "metadata_contributors_person_or_org_identifiers_identifier": (
            facets.metadata_contributors_person_or_org_identifiers_identifier
        ),
        "metadata_contributors_person_or_org_identifiers_scheme": (
            facets.metadata_contributors_person_or_org_identifiers_scheme
        ),
        "metadata_contributors_person_or_org_name": (
            facets.metadata_contributors_person_or_org_name
        ),
        "metadata_contributors_person_or_org_type": (
            facets.metadata_contributors_person_or_org_type
        ),
        "metadata_contributors_role": facets.metadata_contributors_role,
        "metadata_creators_affiliations": facets.metadata_creators_affiliations,
        "metadata_creators_person_or_org_family_name": (
            facets.metadata_creators_person_or_org_family_name
        ),
        "metadata_creators_person_or_org_given_name": (
            facets.metadata_creators_person_or_org_given_name
        ),
        "metadata_creators_person_or_org_identifiers_identifier": (
            facets.metadata_creators_person_or_org_identifiers_identifier
        ),
        "metadata_creators_person_or_org_identifiers_scheme": (
            facets.metadata_creators_person_or_org_identifiers_scheme
        ),
        "metadata_creators_person_or_org_name": (
            facets.metadata_creators_person_or_org_name
        ),
        "metadata_creators_person_or_org_type": (
            facets.metadata_creators_person_or_org_type
        ),
        "metadata_creators_role": facets.metadata_creators_role,
        "metadata_date_issued": facets.metadata_date_issued,
        "metadata_descriptions_cs": facets.metadata_descriptions_cs,
        "metadata_descriptions_en": facets.metadata_descriptions_en,
        "metadata_descriptions": facets.metadata_descriptions,
        "metadata_descriptions_lang": facets.metadata_descriptions_lang,
        "metadata_funding_references_award": facets.metadata_funding_references_award,
        "metadata_funding_references_funder": facets.metadata_funding_references_funder,
        "metadata_other_languages": facets.metadata_other_languages,
        "metadata_primary_language": facets.metadata_primary_language,
        "metadata_publisher_affiliations": facets.metadata_publisher_affiliations,
        "metadata_publisher_person_or_org_family_name": (
            facets.metadata_publisher_person_or_org_family_name
        ),
        "metadata_publisher_person_or_org_given_name": (
            facets.metadata_publisher_person_or_org_given_name
        ),
        "metadata_publisher_person_or_org_identifiers_identifier": (
            facets.metadata_publisher_person_or_org_identifiers_identifier
        ),
        "metadata_publisher_person_or_org_identifiers_scheme": (
            facets.metadata_publisher_person_or_org_identifiers_scheme
        ),
        "metadata_publisher_person_or_org_name": (
            facets.metadata_publisher_person_or_org_name
        ),
        "metadata_publisher_person_or_org_type": (
            facets.metadata_publisher_person_or_org_type
        ),
        "metadata_publisher_role": facets.metadata_publisher_role,
        "metadata_related_resources_contributors_affiliations": (
            facets.metadata_related_resources_contributors_affiliations
        ),
        "metadata_related_resources_contributors_person_or_org_family_name": (
            facets.metadata_related_resources_contributors_person_or_org_family_name
        ),
        "metadata_related_resources_contributors_person_or_org_given_name": (
            facets.metadata_related_resources_contributors_person_or_org_given_name
        ),
        "metadata_related_resources_contributors_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_contributors_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_contributors_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_contributors_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_contributors_person_or_org_name": (
            facets.metadata_related_resources_contributors_person_or_org_name
        ),
        "metadata_related_resources_contributors_person_or_org_type": (
            facets.metadata_related_resources_contributors_person_or_org_type
        ),
        "metadata_related_resources_contributors_role": (
            facets.metadata_related_resources_contributors_role
        ),
        "metadata_related_resources_creators_affiliations": (
            facets.metadata_related_resources_creators_affiliations
        ),
        "metadata_related_resources_creators_person_or_org_family_name": (
            facets.metadata_related_resources_creators_person_or_org_family_name
        ),
        "metadata_related_resources_creators_person_or_org_given_name": (
            facets.metadata_related_resources_creators_person_or_org_given_name
        ),
        "metadata_related_resources_creators_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_creators_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_creators_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_creators_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_creators_person_or_org_name": (
            facets.metadata_related_resources_creators_person_or_org_name
        ),
        "metadata_related_resources_creators_person_or_org_type": (
            facets.metadata_related_resources_creators_person_or_org_type
        ),
        "metadata_related_resources_creators_role": (
            facets.metadata_related_resources_creators_role
        ),
        "metadata_related_resources_identifiers_identifier": (
            facets.metadata_related_resources_identifiers_identifier
        ),
        "metadata_related_resources_identifiers_scheme": (
            facets.metadata_related_resources_identifiers_scheme
        ),
        "metadata_related_resources_publisher_affiliations": (
            facets.metadata_related_resources_publisher_affiliations
        ),
        "metadata_related_resources_publisher_person_or_org_family_name": (
            facets.metadata_related_resources_publisher_person_or_org_family_name
        ),
        "metadata_related_resources_publisher_person_or_org_given_name": (
            facets.metadata_related_resources_publisher_person_or_org_given_name
        ),
        "metadata_related_resources_publisher_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_publisher_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_publisher_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_publisher_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_publisher_person_or_org_name": (
            facets.metadata_related_resources_publisher_person_or_org_name
        ),
        "metadata_related_resources_publisher_person_or_org_type": (
            facets.metadata_related_resources_publisher_person_or_org_type
        ),
        "metadata_related_resources_publisher_role": (
            facets.metadata_related_resources_publisher_role
        ),
        "metadata_related_resources_relation_type": (
            facets.metadata_related_resources_relation_type
        ),
        "metadata_related_resources_resource_url": (
            facets.metadata_related_resources_resource_url
        ),
        "metadata_related_resources_time_references_date": (
            facets.metadata_related_resources_time_references_date
        ),
        "metadata_related_resources_time_references_date_information": (
            facets.metadata_related_resources_time_references_date_information
        ),
        "metadata_related_resources_time_references_date_type": (
            facets.metadata_related_resources_time_references_date_type
        ),
        "metadata_related_resources_type": facets.metadata_related_resources_type,
        "metadata_resource_type": facets.metadata_resource_type,
        "metadata_subjects_classificationCode": (
            facets.metadata_subjects_classificationCode
        ),
        "metadata_subjects_iri": facets.metadata_subjects_iri,
        "metadata_subjects_subject_cs": facets.metadata_subjects_subject_cs,
        "metadata_subjects_subject_en": facets.metadata_subjects_subject_en,
        "metadata_subjects_subject": facets.metadata_subjects_subject,
        "metadata_subjects_subject_lang": facets.metadata_subjects_subject_lang,
        "metadata_subjects_subjectScheme": facets.metadata_subjects_subjectScheme,
        "metadata_terms_of_use_access_rights": (
            facets.metadata_terms_of_use_access_rights
        ),
        "metadata_terms_of_use_descriptions_cs": (
            facets.metadata_terms_of_use_descriptions_cs
        ),
        "metadata_terms_of_use_descriptions_en": (
            facets.metadata_terms_of_use_descriptions_en
        ),
        "metadata_terms_of_use_descriptions": facets.metadata_terms_of_use_descriptions,
        "metadata_terms_of_use_descriptions_lang": (
            facets.metadata_terms_of_use_descriptions_lang
        ),
        "metadata_terms_of_use_licenses": facets.metadata_terms_of_use_licenses,
        "metadata_time_references_date": facets.metadata_time_references_date,
        "metadata_time_references_date_information": (
            facets.metadata_time_references_date_information
        ),
        "metadata_time_references_date_type": facets.metadata_time_references_date_type,
        "metadata_version": facets.metadata_version,
        "state": facets.state,
        "state_timestamp": facets.state_timestamp,
        "record_status": facets.record_status,
        "has_draft": facets.has_draft,
    }


class DatasetsDraftSearchOptions(I18nRDMDraftsSearchOptions):
    """DatasetsDraft search options."""

    facet_groups = {}

    facets = {
        "access_embargo_active": facets.access_embargo_active,
        "access_embargo_until": facets.access_embargo_until,
        "access_files": facets.access_files,
        "access_record": facets.access_record,
        "access_status": facets.access_status,
        "metadata_alternate_identifiers_identifier": (
            facets.metadata_alternate_identifiers_identifier
        ),
        "metadata_alternate_identifiers_scheme": (
            facets.metadata_alternate_identifiers_scheme
        ),
        "metadata_alternate_titles_title_cs": facets.metadata_alternate_titles_title_cs,
        "metadata_alternate_titles_title_en": facets.metadata_alternate_titles_title_en,
        "metadata_alternate_titles_title": facets.metadata_alternate_titles_title,
        "metadata_alternate_titles_title_lang": (
            facets.metadata_alternate_titles_title_lang
        ),
        "metadata_alternate_titles_titleType": (
            facets.metadata_alternate_titles_titleType
        ),
        "metadata_contributors_affiliations": facets.metadata_contributors_affiliations,
        "metadata_contributors_person_or_org_family_name": (
            facets.metadata_contributors_person_or_org_family_name
        ),
        "metadata_contributors_person_or_org_given_name": (
            facets.metadata_contributors_person_or_org_given_name
        ),
        "metadata_contributors_person_or_org_identifiers_identifier": (
            facets.metadata_contributors_person_or_org_identifiers_identifier
        ),
        "metadata_contributors_person_or_org_identifiers_scheme": (
            facets.metadata_contributors_person_or_org_identifiers_scheme
        ),
        "metadata_contributors_person_or_org_name": (
            facets.metadata_contributors_person_or_org_name
        ),
        "metadata_contributors_person_or_org_type": (
            facets.metadata_contributors_person_or_org_type
        ),
        "metadata_contributors_role": facets.metadata_contributors_role,
        "metadata_creators_affiliations": facets.metadata_creators_affiliations,
        "metadata_creators_person_or_org_family_name": (
            facets.metadata_creators_person_or_org_family_name
        ),
        "metadata_creators_person_or_org_given_name": (
            facets.metadata_creators_person_or_org_given_name
        ),
        "metadata_creators_person_or_org_identifiers_identifier": (
            facets.metadata_creators_person_or_org_identifiers_identifier
        ),
        "metadata_creators_person_or_org_identifiers_scheme": (
            facets.metadata_creators_person_or_org_identifiers_scheme
        ),
        "metadata_creators_person_or_org_name": (
            facets.metadata_creators_person_or_org_name
        ),
        "metadata_creators_person_or_org_type": (
            facets.metadata_creators_person_or_org_type
        ),
        "metadata_creators_role": facets.metadata_creators_role,
        "metadata_date_issued": facets.metadata_date_issued,
        "metadata_descriptions_cs": facets.metadata_descriptions_cs,
        "metadata_descriptions_en": facets.metadata_descriptions_en,
        "metadata_descriptions": facets.metadata_descriptions,
        "metadata_descriptions_lang": facets.metadata_descriptions_lang,
        "metadata_funding_references_award": facets.metadata_funding_references_award,
        "metadata_funding_references_funder": facets.metadata_funding_references_funder,
        "metadata_other_languages": facets.metadata_other_languages,
        "metadata_primary_language": facets.metadata_primary_language,
        "metadata_publisher_affiliations": facets.metadata_publisher_affiliations,
        "metadata_publisher_person_or_org_family_name": (
            facets.metadata_publisher_person_or_org_family_name
        ),
        "metadata_publisher_person_or_org_given_name": (
            facets.metadata_publisher_person_or_org_given_name
        ),
        "metadata_publisher_person_or_org_identifiers_identifier": (
            facets.metadata_publisher_person_or_org_identifiers_identifier
        ),
        "metadata_publisher_person_or_org_identifiers_scheme": (
            facets.metadata_publisher_person_or_org_identifiers_scheme
        ),
        "metadata_publisher_person_or_org_name": (
            facets.metadata_publisher_person_or_org_name
        ),
        "metadata_publisher_person_or_org_type": (
            facets.metadata_publisher_person_or_org_type
        ),
        "metadata_publisher_role": facets.metadata_publisher_role,
        "metadata_related_resources_contributors_affiliations": (
            facets.metadata_related_resources_contributors_affiliations
        ),
        "metadata_related_resources_contributors_person_or_org_family_name": (
            facets.metadata_related_resources_contributors_person_or_org_family_name
        ),
        "metadata_related_resources_contributors_person_or_org_given_name": (
            facets.metadata_related_resources_contributors_person_or_org_given_name
        ),
        "metadata_related_resources_contributors_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_contributors_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_contributors_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_contributors_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_contributors_person_or_org_name": (
            facets.metadata_related_resources_contributors_person_or_org_name
        ),
        "metadata_related_resources_contributors_person_or_org_type": (
            facets.metadata_related_resources_contributors_person_or_org_type
        ),
        "metadata_related_resources_contributors_role": (
            facets.metadata_related_resources_contributors_role
        ),
        "metadata_related_resources_creators_affiliations": (
            facets.metadata_related_resources_creators_affiliations
        ),
        "metadata_related_resources_creators_person_or_org_family_name": (
            facets.metadata_related_resources_creators_person_or_org_family_name
        ),
        "metadata_related_resources_creators_person_or_org_given_name": (
            facets.metadata_related_resources_creators_person_or_org_given_name
        ),
        "metadata_related_resources_creators_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_creators_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_creators_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_creators_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_creators_person_or_org_name": (
            facets.metadata_related_resources_creators_person_or_org_name
        ),
        "metadata_related_resources_creators_person_or_org_type": (
            facets.metadata_related_resources_creators_person_or_org_type
        ),
        "metadata_related_resources_creators_role": (
            facets.metadata_related_resources_creators_role
        ),
        "metadata_related_resources_identifiers_identifier": (
            facets.metadata_related_resources_identifiers_identifier
        ),
        "metadata_related_resources_identifiers_scheme": (
            facets.metadata_related_resources_identifiers_scheme
        ),
        "metadata_related_resources_publisher_affiliations": (
            facets.metadata_related_resources_publisher_affiliations
        ),
        "metadata_related_resources_publisher_person_or_org_family_name": (
            facets.metadata_related_resources_publisher_person_or_org_family_name
        ),
        "metadata_related_resources_publisher_person_or_org_given_name": (
            facets.metadata_related_resources_publisher_person_or_org_given_name
        ),
        "metadata_related_resources_publisher_person_or_org_identifiers_identifier": (
            facets.metadata_related_resources_publisher_person_or_org_identifiers_identifier
        ),
        "metadata_related_resources_publisher_person_or_org_identifiers_scheme": (
            facets.metadata_related_resources_publisher_person_or_org_identifiers_scheme
        ),
        "metadata_related_resources_publisher_person_or_org_name": (
            facets.metadata_related_resources_publisher_person_or_org_name
        ),
        "metadata_related_resources_publisher_person_or_org_type": (
            facets.metadata_related_resources_publisher_person_or_org_type
        ),
        "metadata_related_resources_publisher_role": (
            facets.metadata_related_resources_publisher_role
        ),
        "metadata_related_resources_relation_type": (
            facets.metadata_related_resources_relation_type
        ),
        "metadata_related_resources_resource_url": (
            facets.metadata_related_resources_resource_url
        ),
        "metadata_related_resources_time_references_date": (
            facets.metadata_related_resources_time_references_date
        ),
        "metadata_related_resources_time_references_date_information": (
            facets.metadata_related_resources_time_references_date_information
        ),
        "metadata_related_resources_time_references_date_type": (
            facets.metadata_related_resources_time_references_date_type
        ),
        "metadata_related_resources_type": facets.metadata_related_resources_type,
        "metadata_resource_type": facets.metadata_resource_type,
        "metadata_subjects_classificationCode": (
            facets.metadata_subjects_classificationCode
        ),
        "metadata_subjects_iri": facets.metadata_subjects_iri,
        "metadata_subjects_subject_cs": facets.metadata_subjects_subject_cs,
        "metadata_subjects_subject_en": facets.metadata_subjects_subject_en,
        "metadata_subjects_subject": facets.metadata_subjects_subject,
        "metadata_subjects_subject_lang": facets.metadata_subjects_subject_lang,
        "metadata_subjects_subjectScheme": facets.metadata_subjects_subjectScheme,
        "metadata_terms_of_use_access_rights": (
            facets.metadata_terms_of_use_access_rights
        ),
        "metadata_terms_of_use_descriptions_cs": (
            facets.metadata_terms_of_use_descriptions_cs
        ),
        "metadata_terms_of_use_descriptions_en": (
            facets.metadata_terms_of_use_descriptions_en
        ),
        "metadata_terms_of_use_descriptions": facets.metadata_terms_of_use_descriptions,
        "metadata_terms_of_use_descriptions_lang": (
            facets.metadata_terms_of_use_descriptions_lang
        ),
        "metadata_terms_of_use_licenses": facets.metadata_terms_of_use_licenses,
        "metadata_time_references_date": facets.metadata_time_references_date,
        "metadata_time_references_date_information": (
            facets.metadata_time_references_date_information
        ),
        "metadata_time_references_date_type": facets.metadata_time_references_date_type,
        "metadata_version": facets.metadata_version,
        "state": facets.state,
        "state_timestamp": facets.state_timestamp,
        "expires_at": facets.expires_at,
        "fork_version_id": facets.fork_version_id,
        **getattr(I18nRDMDraftsSearchOptions, "facets", {}),
        "record_status": facets.record_status,
        "has_draft": facets.has_draft,
    }
