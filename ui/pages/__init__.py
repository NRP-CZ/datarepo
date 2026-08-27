from collections.abc import Mapping
from oarepo_ui.resources import TemplatePageUIResource, TemplatePageUIResourceConfig

class PagesUIResourceConfig(TemplatePageUIResourceConfig):
    template_folder = "templates"
    url_prefix = "/"
    blueprint_name = "pages_ui"
    application_id = "pages"

    pages: Mapping[str,str] = {
        "get-access": "GetAccess"
    }


class PagesUIResource(TemplatePageUIResource):
    pass


def create_blueprint(app):
    """Register blueprint for this resource."""
    blueprint = PagesUIResource(PagesUIResourceConfig()).as_blueprint()
    return blueprint
