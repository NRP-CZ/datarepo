from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    ".",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "datasets_search": "./js/datasets/search/index.js",
                "datasets_deposit_form": "./js/datasets/forms/index.js",
            },
            dependencies={},
            devDependencies={},
            aliases={
                "@js/datasets": "./js/datasets"
            },
        )
    },
)
