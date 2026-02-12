#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource component for community memberships."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flask import g
from invenio_communities.proxies import current_communities
from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem


# TODO: MAJOR TODO: This is stub implementation. I don't know how we will handle community submission
# and who will be allowed to do so. This is mainly for testing of community header selector
class CommunitiesMembershipsComponent(UIResourceComponent):
    """Pass current identity's community memberships to form config."""

    def form_config(  # noqa: PLR0913  too many arguments
        self,
        *,
        api_record: RecordItem,  # noqa: ARG002
        record: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        form_config: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Add current identity's community memberships to form config."""
        memberships = current_communities.service.members.read_memberships(g.identity)
        form_config["user_communities_memberships"] = {
            id: role for (id, role) in memberships["memberships"]
        }
