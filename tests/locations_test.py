# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Tests for the `Geographic locations` record-detail sidebar.

The template is rendered against a bare Jinja environment rather than a booted
Invenio app: it only needs `_`, `webpack` and `record_ui`. The wiring into
`APP_RDM_DETAIL_SIDE_BAR_TEMPLATES` is asserted separately.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader
from markupsafe import Markup

REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates" / "semantic-ui"
TEMPLATE = "datarepo/records/details/side_bar/locations.html"

POINT = {
    "place": "Prostějov Center",
    "description": "Standard 2D GeoJSON Point.",
    "geometry": {"type": "Point", "coordinates": [17.1118, 49.4718]},
}
WKT_POLYGON = {
    "place": "Olomouc Region",
    "geometry": "POLYGON ((16.8 49.3, 17.8 49.3, 17.8 50.3, 16.8 50.3, 16.8 49.3))",
}


class _Webpack:
    """Stand-in for Invenio's `webpack` proxy, recording what the template asks for."""

    def __init__(self) -> None:
        self.requested: list[str] = []

    def __getitem__(self, key: str) -> Markup:
        self.requested.append(key)
        # Invenio returns pre-rendered markup here, so mirror that.
        return Markup(f"<!-- {key} -->")  # noqa: S704


@pytest.fixture
def render():
    """Render the sidebar template for a given list of UI-serialized locations."""

    def _render(locations):
        env = Environment(
            loader=ChoiceLoader([FileSystemLoader(TEMPLATE_DIR), DictLoader({})]),
            autoescape=True,
        )
        env.globals["_"] = lambda message: message
        webpack = _Webpack()
        html = env.get_template(TEMPLATE).render(
            record_ui={"ui": {"locations": locations} if locations is not None else {}},
            webpack=webpack,
        )
        return html, webpack

    return _render


def _data_locations(html: str) -> list[dict]:
    """Pull the serialized payload back out of the map mount point."""
    match = re.search(r"id=\"record-locations-map\"[^>]*data-locations='([^']*)'", html)
    assert match, "no data-locations payload found on #record-locations-map"
    from html import unescape

    return json.loads(unescape(match.group(1)))


def test_mount_point_and_anchor_ids_are_stable(render):
    """Existing anchors must not drift when replacing the upstream template."""
    html, _ = render([POINT])

    assert 'id="record-locations"' in html
    assert 'id="record-locations-map"' in html
    assert 'id="record-locations-list"' in html


def test_map_receives_every_location_as_json(render):
    html, _ = render([POINT, WKT_POLYGON])

    payload = _data_locations(html)
    assert [location["place"] for location in payload] == [
        "Prostějov Center",
        "Olomouc Region",
    ]
    # WKT stays a raw string, GeoJSON stays an object - the client handles both.
    assert isinstance(payload[0]["geometry"], dict)
    assert isinstance(payload[1]["geometry"], str)


def test_text_fallback_lists_each_place(render):
    html, _ = render([POINT, WKT_POLYGON])

    assert html.count('class="record-locations-point-reference"') == 2
    assert "Prostějov Center" in html
    assert "Olomouc Region" in html


def test_bundles_are_requested(render):
    _, webpack = render([POINT])

    assert set(webpack.requested) == {
        "locations_geometry.js",
        "locations_map.js",
        "locations_point.js",
        "locations_map.css",
    }


def test_metadata_is_escaped(render):
    html, _ = render([{**POINT, "place": "<script>alert(1)</script>"}])

    assert "<script>alert(1)</script>" not in html
    assert _data_locations(html)[0]["place"] == "<script>alert(1)</script>"


@pytest.mark.parametrize("locations", [None, []], ids=["no locations key", "empty list"])
def test_block_is_omitted_when_there_is_no_coverage(render, locations):
    html, _ = render(locations)

    assert "record-locations" not in html
    assert html.strip() == ""


def test_template_is_registered_in_the_sidebar():
    config = (REPO_ROOT / "invenio.cfg").read_text(encoding="utf-8")
    sidebar = re.search(r"APP_RDM_DETAIL_SIDE_BAR_TEMPLATES\s*=\s*\[(.*?)\]", config, re.DOTALL)
    assert sidebar, "APP_RDM_DETAIL_SIDE_BAR_TEMPLATES not found in invenio.cfg"

    entries = [
        line.strip().strip(",").strip('"')
        for line in sidebar.group(1).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert TEMPLATE in entries
    assert "invenio_app_rdm/records/details/side_bar/locations.html" not in entries
