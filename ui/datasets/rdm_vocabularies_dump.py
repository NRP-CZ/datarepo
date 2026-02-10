#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource component for vocabulary search."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_app_rdm.records_ui.views.deposits import (
    VocabulariesOptions,
)
from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem


class RDMVocabularyOptionsComponent(UIResourceComponent):
    """Pass RDM vocabulary fixtures to form config."""

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
        """Add smaller RDM vocabularies to form config."""
        form_config["vocabularies"] = VocabulariesOptions().dump()  # pragma: no cover
