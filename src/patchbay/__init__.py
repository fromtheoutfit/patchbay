"""patchbay-core: the contracts, host and CLI that patchbay-<instrument> adapters plug into.

The package exports its version and nothing else yet; the version is the one in pyproject.toml,
read from the installed distribution's metadata so there is one place it is written.
"""

from importlib.metadata import version

__version__ = version("patchbay-core")

__all__ = ["__version__"]
