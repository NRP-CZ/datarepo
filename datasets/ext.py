import re
from functools import cached_property

from invenio_rdm_records.services.pids import PIDManager, PIDsService
from oarepo_requests.proxies import current_oarepo_requests_service
from oarepo_requests.resources.draft.config import DraftRecordRequestsResourceConfig
from oarepo_requests.resources.draft.types.config import DraftRequestTypesResourceConfig

from datasets import config


class DatasetsExt:

    def __init__(self, app=None):

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app

        self.init_config(app)
        if not self.is_inherited():
            self.register_flask_extension(app)

        for method in dir(self):
            if method.startswith("init_app_callback_"):
                getattr(self, method)(app)

    def register_flask_extension(self, app):

        app.extensions["datasets"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for identifier in dir(config):
            if re.match("^[A-Z_0-9]*$", identifier) and not identifier.startswith("_"):
                if isinstance(app.config.get(identifier), list):
                    app.config[identifier] += getattr(config, identifier)
                elif isinstance(app.config.get(identifier), dict):
                    for k, v in getattr(config, identifier).items():
                        if k not in app.config[identifier]:
                            app.config[identifier][k] = v
                else:
                    app.config.setdefault(identifier, getattr(config, identifier))

    def is_inherited(self):
        from importlib_metadata import entry_points

        ext_class = type(self)
        for ep in entry_points(group="invenio_base.apps"):
            loaded = ep.load()
            if loaded is not ext_class and issubclass(ext_class, loaded):
                return True
        for ep in entry_points(group="invenio_base.api_apps"):
            loaded = ep.load()
            if loaded is not ext_class and issubclass(ext_class, loaded):
                return True
        return False

    @cached_property
    def service_records(self):
        service_config = config.DATASETS_RECORD_SERVICE_CONFIG
        if hasattr(service_config, "build"):
            config_class = service_config.build(self.app)
        else:
            config_class = service_config()

        service_kwargs = {
            "pids_service": PIDsService(config_class, PIDManager),
            "config": config_class,
        }
        return config.DATASETS_RECORD_SERVICE_CLASS(
            **service_kwargs,
            files_service=self.service_files,
            draft_files_service=self.service_draft_files,
        )

    @cached_property
    def resource_records(self):
        return config.DATASETS_RECORD_RESOURCE_CLASS(
            service=self.service_records,
            config=config.DATASETS_RECORD_RESOURCE_CONFIG(),
        )

    @cached_property
    def service_record_requests(self):
        return config.DATASETS_REQUESTS_SERVICE_CLASS(
            record_service=self.service_records,
            oarepo_requests_service=current_oarepo_requests_service,
        )

    @cached_property
    def resource_record_requests(self):
        return config.DATASETS_REQUESTS_RESOURCE_CLASS(
            service=self.service_record_requests,
            config=config.DATASETS_RECORD_RESOURCE_CONFIG(),
            record_requests_config=DraftRecordRequestsResourceConfig(),
        )

    @cached_property
    def service_record_request_types(self):
        return config.DATASETS_REQUEST_TYPES_SERVICE_CLASS(
            record_service=self.service_records,
            oarepo_requests_service=current_oarepo_requests_service,
        )

    @cached_property
    def resource_record_request_types(self):
        return config.DATASETS_REQUEST_TYPES_RESOURCE_CLASS(
            service=self.service_record_request_types,
            config=config.DATASETS_RECORD_RESOURCE_CONFIG(),
            record_requests_config=DraftRequestTypesResourceConfig(),
        )

    def init_app_callback_rdm_models(self, app):

        app.config.setdefault("GLOBAL_SEARCH_MODELS", [])
        for cfg in app.config["GLOBAL_SEARCH_MODELS"]:
            if cfg["model_service"] == RDM_MODEL_CONFIG["model_service"]:
                break
        else:
            app.config["GLOBAL_SEARCH_MODELS"].append(RDM_MODEL_CONFIG)

        app.config.setdefault("RDM_MODELS", [])
        for cfg in app.config["RDM_MODELS"]:
            if cfg["model_service"] == RDM_MODEL_CONFIG["model_service"]:
                break
        else:
            app.config["RDM_MODELS"].append(RDM_MODEL_CONFIG)

    @cached_property
    def service_files(self):
        service_config = config.DATASETS_FILES_SERVICE_CONFIG
        if hasattr(service_config, "build"):
            config_class = service_config.build(self.app)
        else:
            config_class = service_config()

        service_kwargs = {"config": config_class}
        return config.DATASETS_FILES_SERVICE_CLASS(
            **service_kwargs,
        )

    @cached_property
    def resource_files(self):
        return config.DATASETS_FILES_RESOURCE_CLASS(
            service=self.service_files,
            config=config.DATASETS_FILES_RESOURCE_CONFIG(),
        )

    @cached_property
    def service_draft_files(self):
        service_config = config.DATASETS_DRAFT_FILES_SERVICE_CONFIG
        if hasattr(service_config, "build"):
            config_class = service_config.build(self.app)
        else:
            config_class = service_config()

        service_kwargs = {"config": config_class}
        return config.DATASETS_DRAFT_FILES_SERVICE_CLASS(
            **service_kwargs,
        )

    @cached_property
    def resource_draft_files(self):
        return config.DATASETS_DRAFT_FILES_RESOURCE_CLASS(
            service=self.service_draft_files,
            config=config.DATASETS_DRAFT_FILES_RESOURCE_CONFIG(),
        )


RDM_MODEL_CONFIG = {  # allows merging stuff from other builders
    "service_id": "datasets",
    # deprecated
    "model_service": "datasets.services.records.service.DatasetsService",
    # deprecated
    "service_config": "datasets.services.records.config.DatasetsServiceConfig",
    "api_service": "datasets.services.records.service.DatasetsService",
    "api_service_config": "datasets.services.records.config.DatasetsServiceConfig",
    "api_resource": "datasets.resources.records.resource.DatasetsResource",
    "api_resource_config": "datasets.resources.records.config.DatasetsResourceConfig",
    "ui_resource_config": "ui.datasets.DatasetsUIResourceConfig",
    "record_cls": "datasets.records.api.DatasetsRecord",
    "pid_type": "dtsts",
    "draft_cls": "datasets.records.api.DatasetsDraft",
}
