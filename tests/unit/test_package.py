"""The package's surface is __all__, and its distribution carries the license."""

import importlib.metadata
import types

import patchbay
from patchbay import contracts, errors, events, models


def test_public_names_are_in_all() -> None:
    """Every name the package binds without a leading underscore is one __all__ exports.

    Its submodules aside: importing `patchbay.errors` binds `errors` on the package, the import
    system's doing rather than an export, and `from patchbay import *` does not import them.
    """
    public = {
        name
        for name, value in vars(patchbay).items()
        if not name.startswith("_") and not isinstance(value, types.ModuleType)
    }
    assert public <= set(patchbay.__all__)


def test_every_name_in_all_resolves() -> None:
    """__all__ names only what the package binds, each once, so `import *` cannot fail."""
    assert len(set(patchbay.__all__)) == len(patchbay.__all__)
    assert all(hasattr(patchbay, name) for name in patchbay.__all__)


def test_the_package_re_exports_the_contract_surface() -> None:
    """Each name __all__ exports is the object its module defines, not a copy or a second type."""
    for name in patchbay.__all__:
        if name == "__version__":
            continue
        homes = [m for m in (contracts, errors, events, models) if name in vars(m)]
        assert homes, name
        assert all(getattr(patchbay, name) is vars(m)[name] for m in homes), name


def test_distribution_names_its_license_file() -> None:
    """The installed metadata states the license and names the LICENSE file shipped with it."""
    metadata = importlib.metadata.metadata("patchbay-core")
    assert metadata["License-Expression"] == "MIT"
    assert metadata.get_all("License-File") == ["LICENSE"]
