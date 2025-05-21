from oarepo_runtime.records.dumpers.multilingual_dumper import MultilingualDumper


class MultilingualSearchDumperExt(MultilingualDumper):
    """Multilingual search dumper."""

    paths = [
        "/metadata/alternate_titles/title",
        "/metadata/descriptions",
        "/metadata/subjects/subject",
        "/metadata/terms_of_use/descriptions",
    ]
    SUPPORTED_LANGS = ["cs", "en"]

    def dump(self, record, data):
        super().dump(record, data)

    def load(self, record, data):
        super().load(record, data)
