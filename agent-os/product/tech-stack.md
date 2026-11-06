# Tech stack

The decisions already made, in issue #1, and implemented by the toolchain spec (issue #2,
`agent-os/specs/2026-11-05-2018-toolchain-ruff-mypy-pytest-full-gate/`), whose `shape.md` holds
each configuration choice as a Decision with its reason. Each is one line here; `pyproject.toml`
is the configuration, and the standard that names it is
`agent-os/standards/base/python/toolchain.md`, written in `patchbay-standards` from that code and
synced in, which every spec here includes (Step 5a of `/agent-os:shape-spec`).

- **uv** manages the project and **`uv_build`** builds it (`pyproject.toml` already says so; the
  lockfile is committed). Tools the gate runs are pinned exactly in `pyproject.toml`'s
  `[dependency-groups] dev`, resolved in `uv.lock`, and run through `uv run --locked`: for a
  package the lockfile is the pin, and mypy and pytest need the project installed, which `uvx`
  cannot give them (issue #2 corrected issue #1's `uvx`). uv itself is pinned by `[tool.uv]
  required-version`, which CI's setup-uv reads too.
- **Python >= 3.12** (`requires-python`; `.python-version` pins the interpreter).
- **ruff** for linting and formatting, with `select = ["ALL"]`; every disabled rule is named with
  its reason.
- **mypy --strict** over the package and the tests.
- **pytest** for tests and **hypothesis** for property-based ones.
- **pydantic v2** for every contract that crosses a boundary.
- **typer** for the CLI.
- **src layout**: `src/patchbay/`, typed (`py.typed`); distribution `patchbay-core`, import
  `patchbay`.
