# Tech stack

The decisions already made, in issue #1, for the toolchain spec to implement. Each is one line
here; the spec that implements it writes the configuration and the standard that names it.

- **uv** manages the project and **`uv_build`** builds it (`pyproject.toml` already says so; the
  lockfile is committed). Tools the gate runs are pinned in `scripts/gate.sh` and run through
  `uvx`, installing nothing into the project.
- **Python >= 3.12** (`requires-python`; `.python-version` pins the interpreter).
- **ruff** for linting and formatting, with `select = ["ALL"]`; every disabled rule is named with
  its reason.
- **mypy --strict** over the package and the tests.
- **pytest** for tests and **hypothesis** for property-based ones.
- **pydantic v2** for every contract that crosses a boundary.
- **typer** for the CLI.
- **src layout**: `src/patchbay/`, typed (`py.typed`); distribution `patchbay-core`, import
  `patchbay`.
