from oarepo_ui.resources.config import TemplatePageUIResourceConfig
from oarepo_ui.resources.resource import TemplatePageUIResource
from flask import redirect


class ComponentsResourceConfig(TemplatePageUIResourceConfig):
    url_prefix = "/"
    blueprint_name = "components"
    template_folder = "templates"


def create_blueprint(app):
    """Register blueprint for this resource."""
    # TODO: Hacky solution to avoid error in invenio-communities where link is hardcoded
    # they promised to correct this soon
    app.add_url_rule(
        "/fake-link",
        endpoint="invenio_app_rdm_users.communities",
        view_func=lambda: redirect("/me/communities/"),
    )

    return TemplatePageUIResource(ComponentsResourceConfig()).as_blueprint()
