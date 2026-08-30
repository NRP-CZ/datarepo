#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT
#
# Wrapper script for oarepo-cli repository commands.
# Copy this file as "run.sh" to your repository project root.
# The file is added automatically when creating a new repository
# using the oarepo-cli "repository init" command.
#
# This script:
# - Sets up a local .tools/venv (using uv) on first run
# - Installs oarepo-cli into that venv
# - Forwards all arguments to "oarepo-cli repository <args>"
#
# Usage:
#   ./run.sh install       # runs: oarepo-cli repository install
#   ./run.sh run           # runs: oarepo-cli repository run
#   ./run.sh self-update   # removes .tools/venv and reinstalls oarepo-cli
#

set -euo pipefail

# OARepo packages and the CESNET-patched invenio-cli build (which oarepo-cli
# requires) live in the CESNET GitLab PyPI registry, not on public PyPI. uv
# gives an extra index higher priority than the default index, so invenio-cli
# resolves to the patched build here. Overridable via the environment.
export UV_EXTRA_INDEX_URL="${UV_EXTRA_INDEX_URL:-https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple}"
export PIP_EXTRA_INDEX_URL="${PIP_EXTRA_INDEX_URL:-https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${SCRIPT_DIR}/.tools"
VENV_DIR="${TOOLS_DIR}/venv"
OAREPO_CLI="${VENV_DIR}/bin/oarepo-cli"

# Handle self-update: remove venv and reinstall
if [[ "${1:-}" == "self-update" ]]; then
    echo "🔄 Self-updating oarepo-cli..." >&2
    if [[ -d "${TOOLS_DIR}" ]]; then
        echo "   Removing ${TOOLS_DIR}..." >&2
        rm -rf "${TOOLS_DIR}"
    fi
    shift  # Remove "self-update" from arguments
fi

# Check if we need to set up the venv
if [[ ! -d "${TOOLS_DIR}" ]] || [[ ! -f "${OAREPO_CLI}" ]]; then
    echo "🔧 Setting up oarepo-cli (first run or after self-update)..." >&2

    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        echo "❌ Error: 'uv' is not installed or not in PATH." >&2
        echo "   Install it with: pip install uv" >&2
        echo "   Or visit: https://github.com/astral-sh/uv" >&2
        exit 1
    fi

    # Create tools directory if needed
    mkdir -p "${TOOLS_DIR}"

    # Create venv with uv
    echo "   Creating virtual environment in ${VENV_DIR}..." >&2
    uv venv "${VENV_DIR}" --python 3.14

    # Install oarepo-cli
    echo "   Installing oarepo-cli..." >&2
    uv pip install --python "${VENV_DIR}/bin/python" oarepo-cli

    echo "✅ oarepo-cli setup complete!" >&2
fi

# Run oarepo-cli with "repository" subcommand and forwarded arguments
exec "${OAREPO_CLI}" repository "$@"
