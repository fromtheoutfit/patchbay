"""patchbay-core: the contracts, host and CLI that patchbay-<instrument> adapters plug into.

The package exports its version and nothing else yet; the version is the one in pyproject.toml,
read from the installed distribution's metadata so there is one place it is written.

Import it installed (`uv sync`): from a bare src/ on sys.path there is no distribution to read,
so importlib.metadata raises PackageNotFoundError rather than the package inventing a version.
"""

import importlib.metadata as _metadata

__version__ = _metadata.version("patchbay-core")

__all__ = ["__version__"]
