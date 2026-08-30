# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Entry point for debugging the repository under a Python debugger."""

from __future__ import annotations

from invenio_app.cli import cli

if __name__ == "__main__":
    cli.main()
