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
    def create_url_rules(self) -> list:
        """Route /get-access to a semantic handler name."""
        from flask_resources import route

        return [route("GET", "get-access", self.get_access)]

    def get_access(self) -> str:
        """Render the standalone-submitter onboarding page."""
        return self.render(page="GetAccess")


def create_blueprint(app):
    """Register blueprint for this resource."""
    blueprint = PagesUIResource(PagesUIResourceConfig()).as_blueprint()
    return blueprint
