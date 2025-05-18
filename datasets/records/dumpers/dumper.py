from datasets.records.dumpers.edtf import (
    DatasetsDraftEDTFIntervalDumperExt,
    DatasetsEDTFIntervalDumperExt,
)
from datasets.records.dumpers.multilingual import MultilingualSearchDumperExt
from oarepo_runtime.records.dumpers import SearchDumper
from oarepo_runtime.records.systemfields.mapping import SystemFieldDumperExt


class DatasetsDumper(SearchDumper):
    """DatasetsRecord opensearch dumper."""

    extensions = [
        SystemFieldDumperExt(),
        MultilingualSearchDumperExt(),
        DatasetsEDTFIntervalDumperExt(),
    ]


class DatasetsDraftDumper(SearchDumper):
    """DatasetsDraft opensearch dumper."""

    extensions = [
        SystemFieldDumperExt(),
        MultilingualSearchDumperExt(),
        DatasetsDraftEDTFIntervalDumperExt(),
    ]
