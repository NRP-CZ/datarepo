from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_records_permissions.generators import AuthenticatedUser, SystemProcess
from oarepo.config.communities import DefaultCommunitiesPermissionPolicy

if TYPE_CHECKING:
    pass


class DataSetsCommunitiesPermission(DefaultCommunitiesPermissionPolicy):
    # called during community-submission submit request
    # and in invenio_communities.communities.resources.ui_schema.UICommunitySchema.get_permissions; in community search at least
    can_submit_record = [SystemProcess(), AuthenticatedUser()]
    can_manage_children = [SystemProcess(), AuthenticatedUser()]
    can_set_theme = [SystemProcess(), AuthenticatedUser()]
