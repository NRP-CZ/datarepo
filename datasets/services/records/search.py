from oarepo_runtime.services.search import (
    I18nRDMDraftsSearchOptions,
    I18nRDMSearchOptions,
)

from . import facets


class DatasetsSearchOptions(I18nRDMSearchOptions):
    """DatasetsRecord search options."""

    facet_groups = {}

    facets = {
        "access_embargo_active": facets.access_embargo_active,
        "access_embargo_until": facets.access_embargo_until,
        "access_files": facets.access_files,
        "access_record": facets.access_record,
        "access_status": facets.access_status,
        "metadata_languages": facets.metadata_languages,
        "metadata_version": facets.metadata_version,
        "state": facets.state,
        "state_timestamp": facets.state_timestamp,
        **getattr(I18nRDMSearchOptions, "facets", {}),
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
        "metadata_languages": facets.metadata_languages,
        "metadata_version": facets.metadata_version,
        "state": facets.state,
        "state_timestamp": facets.state_timestamp,
        "expires_at": facets.expires_at,
        "fork_version_id": facets.fork_version_id,
        **getattr(I18nRDMDraftsSearchOptions, "facets", {}),
        "record_status": facets.record_status,
        "has_draft": facets.has_draft,
    }
