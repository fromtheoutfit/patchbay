"""The package's version is pyproject.toml's, and is a release segment."""

import re
import tomllib
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

import patchbay

# A PEP 440 release segment: dotted non-negative integers. The pattern the version is held to.
_RELEASE = re.compile(r"\d+(\.\d+)*")

_PYPROJECT = Path(__file__).parents[2] / "pyproject.toml"


def test_version_matches_pyproject() -> None:
    """__version__ is the [project] version, read from the metadata of the installed package."""
    with _PYPROJECT.open("rb") as f:
        project = tomllib.load(f)["project"]
    assert patchbay.__version__ == project["version"]


def test_version_is_a_release_segment() -> None:
    """The version is dotted integers, nothing else."""
    assert _RELEASE.fullmatch(patchbay.__version__)


@given(st.tuples(st.integers(min_value=0), st.integers(min_value=0), st.integers(min_value=0)))
def test_release_pattern_accepts_every_dotted_triple(parts: tuple[int, int, int]) -> None:
    """Any major.minor.patch of non-negative integers is a release segment."""
    assert _RELEASE.fullmatch(".".join(str(p) for p in parts))


@given(st.text(min_size=1).filter(lambda s: not s.isdigit()))
def test_release_pattern_rejects_a_non_numeric_segment(segment: str) -> None:
    """A segment that is not all digits is not a release segment, alone or after a release."""
    assert not _RELEASE.fullmatch(segment)
    assert not _RELEASE.fullmatch(f"1.0.{segment}")
