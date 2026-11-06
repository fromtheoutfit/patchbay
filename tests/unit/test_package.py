"""The package's surface is __all__, and its distribution carries the license."""

import importlib.metadata

import patchbay


def test_public_names_are_in_all() -> None:
    """Every name the package binds without a leading underscore is one __all__ exports."""
    public = {name for name in vars(patchbay) if not name.startswith("_")}
    assert public <= set(patchbay.__all__)


def test_distribution_names_its_license_file() -> None:
    """The installed metadata states the license and names the LICENSE file shipped with it."""
    metadata = importlib.metadata.metadata("patchbay-core")
    assert metadata["License-Expression"] == "MIT"
    assert metadata.get_all("License-File") == ["LICENSE"]
