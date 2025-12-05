"""Compatibility filter for nice YAML rendering across Ansible releases."""

from __future__ import annotations

from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display

try:  # pragma: no cover - availability depends on the runtime
    from ansible.release import __version__ as _ANSIBLE_VERSION
except Exception:  # pragma: no cover
    _ANSIBLE_VERSION = None

try:  # pragma: no cover - import location differs depending on version
    from packaging.version import Version
except Exception:  # pragma: no cover
    Version = None

try:  # pragma: no cover - import location differs depending on version
    from ansible_collections.community.general.plugins.filter.core import (  # type: ignore
        to_nice_yaml as _community_to_nice_yaml,
    )
except ImportError:  # pragma: no cover
    try:
        from ansible_collections.community.general.plugins.filter.to_yaml import (  # type: ignore
            to_nice_yaml as _community_to_nice_yaml,
        )
    except ImportError:  # pragma: no cover
        _community_to_nice_yaml = None

try:  # pragma: no cover - Ansible < 2.12 ships this implementation
    from ansible.plugins.filter.core import to_nice_yaml as _legacy_to_nice_yaml  # type: ignore
except ImportError:  # pragma: no cover
    _legacy_to_nice_yaml = None

_DISPLAY = Display()
_WARNED_MISSING_COMMUNITY_FILTER = False


def _core_version_gt_219():
    if Version is None or _ANSIBLE_VERSION is None:
        return False
    try:
        return Version(_ANSIBLE_VERSION) > Version("2.19.0")
    except Exception:  # pragma: no cover - defensive fallback
        return False


_CORE_VERSION_GT_219 = _core_version_gt_219()


def _warn_about_missing_community_filter():
    global _WARNED_MISSING_COMMUNITY_FILTER
    if (
        _WARNED_MISSING_COMMUNITY_FILTER
        or not _CORE_VERSION_GT_219
        or _community_to_nice_yaml is not None
    ):
        return

    _WARNED_MISSING_COMMUNITY_FILTER = True
    version_display = _ANSIBLE_VERSION or "unknown version"
    _DISPLAY.warning(
        (
            "teamapps.general.to_nice_yaml detected ansible-core {version} without community.general.to_nice_yaml. "
            "This combination may dump encrypted Ansible Vault values in plain text. "
            "Install the community.general collection to restore the safer filter implementation. "
            "(See https://github.com/ansible/ansible/issues/85722)"
        ).format(version=version_display)
    )


def _ensure_callable():
    if _community_to_nice_yaml is not None:
        return _community_to_nice_yaml
    if _legacy_to_nice_yaml is not None:
        _warn_about_missing_community_filter()
        return _legacy_to_nice_yaml
    raise AnsibleFilterError(
        "Unable to locate either community.general.to_nice_yaml or the legacy to_nice_yaml filter. "
        "Install a recent community.general collection to continue."
    )


def to_nice_yaml(value, *args, **kwargs):
    """Render value as nice YAML via whichever implementation is available."""

    handler = _ensure_callable()
    return handler(value, *args, **kwargs)


class FilterModule(object):
    """Expose the compatibility filter under predictable names."""

    def filters(self):
        return {
            "teamapps.general.to_nice_yaml": to_nice_yaml,
            "to_nice_yaml": to_nice_yaml,
        }
