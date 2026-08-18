from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "get_access": "./js/get_access/index.js",
            },
            "dependencies": {},
            "aliases": {
                # "@js/datasets": "./js/datasets"
            },
        }
    },
)
