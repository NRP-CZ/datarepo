import re

_ORJK_RE = re.compile(r"^orjk:", re.IGNORECASE)


def is_orjk(value):
    return isinstance(value, str) and _ORJK_RE.match(value.strip()) is not None


def is_parent_id(value):
    return True


def normalize_orjk(value):
    return value.strip().lower()


def normalize_parent_id(value):
    return value.strip().lower() if isinstance(value, str) else value


def orjk_scheme():
    return {
        "validator": is_orjk,
        "normalizer": normalize_orjk,
    }


def parent_id_scheme():
    return {
        "validator": is_parent_id,
        "normalizer": normalize_parent_id,
    }
