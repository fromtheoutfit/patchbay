"""The package's version is pyproject.toml's, and is a release segment."""

import re
import tomllib

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

import patchbay

# A PEP 440 release segment: dotted non-negative integers. The pattern the version is held to.
# [0-9], not \d: \d takes any Unicode decimal digit, such as ARABIC-INDIC DIGIT ONE (U+0661), and
# a release segment is ASCII digits.
_RELEASE = re.compile(r"[0-9]+(\.[0-9]+)*")


def test_version_matches_pyproject(pytestconfig: pytest.Config) -> None:
    """__version__ is the [project] version, read from the metadata of the installed package.

    pyproject.toml is read from pytest's rootdir, the directory of the file pytest took its own
    configuration from, so the test reads the tree it runs in wherever this file sits.
    """
    with (pytestconfig.rootpath / "pyproject.toml").open("rb") as f:
        project = tomllib.load(f)["project"]
    assert patchbay.__version__ == project["version"]


def test_version_is_a_release_segment() -> None:
    """The version is dotted integers, nothing else."""
    assert _RELEASE.fullmatch(patchbay.__version__)


@given(st.tuples(st.integers(min_value=0), st.integers(min_value=0), st.integers(min_value=0)))
def test_release_pattern_accepts_every_dotted_triple(parts: tuple[int, int, int]) -> None:
    """Any major.minor.patch of non-negative integers is a release segment."""
    assert _RELEASE.fullmatch(".".join(str(p) for p in parts))


@given(st.text(min_size=1).filter(lambda s: "." not in s and not (s.isascii() and s.isdigit())))
@example("\u0661\u0660")  # Arabic-Indic ten: decimal digits, not ASCII ones, tried on every run
def test_release_pattern_rejects_a_non_numeric_segment(segment: str) -> None:
    """One segment, no dot, not all ASCII digits, is not a release segment, alone or after one."""
    assert not _RELEASE.fullmatch(segment)
    assert not _RELEASE.fullmatch(f"1.0.{segment}")
