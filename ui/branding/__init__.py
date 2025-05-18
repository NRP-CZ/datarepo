from pathlib import Path

from flask import Blueprint


def create_blueprint(app):
    """Register blueprint for this resource."""
    template_folder = Path(__file__).parent.joinpath("templates").resolve()

    return Blueprint(
        "branding",
        __name__,
        url_prefix="/",
        template_folder=str(template_folder),
    )
