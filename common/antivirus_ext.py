from invenio_records_resources.services.files.processors import FileProcessor
from invenio_records_resources.services.files.config import FileServiceConfig
from typing import override

class AntivirusFileProcessor(FileProcessor):

    @override
    def can_process(self, file_record):
        """Determine if this processor can process a given file record."""
        return True

    @override
    def process(self, file_record):
        """Process a file."""
        print("file antivirus processing....")

class AntivirusFileProcessorsMixin:
    file_processors = [
        *FileServiceConfig.file_processors,
        AntivirusFileProcessor()
    ]