

def create_api_blueprint(app):
    """Create DatasetsFileDraft blueprint."""
    blueprint = app.extensions["datasets"].resource_draft_files.as_blueprint()
    blueprint.record_once(init_create_api_blueprint)

    # calls record_once for all other functions starting with "init_addons_"
    # https://stackoverflow.com/questions/58785162/how-can-i-call-function-with-string-value-that-equals-to-function-name
    funcs = globals()
    funcs = [
        v
        for k, v in funcs.items()
        if k.startswith("init_addons_datasets_file_draft") and callable(v)
    ]
    for func in funcs:
        blueprint.record_once(func)

    return blueprint


def init_create_api_blueprint(state):
    """Init app."""
    app = state.app
    ext = app.extensions["datasets"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(
        ext.service_draft_files, service_id=ext.service_draft_files.config.service_id
    )

    # Register indexer
    if hasattr(ext.service_draft_files, "indexer"):
        iregistry = app.extensions["invenio-indexer"].registry
        iregistry.register(
            ext.service_draft_files.indexer,
            indexer_id=ext.service_draft_files.config.service_id,
        )
