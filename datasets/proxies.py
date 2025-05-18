from flask import current_app
from werkzeug.local import LocalProxy


def _ext_proxy(attr):
    return LocalProxy(lambda: getattr(current_app.extensions["datasets"], attr))


current_service = _ext_proxy("service_records")
"""Proxy to the instantiated service."""


current_resource = _ext_proxy("resource_records")
"""Proxy to the instantiated resource."""
