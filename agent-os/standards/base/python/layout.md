# Layout

Where everything in a patchbay package lives: its modules, the subpackage its consumers' tests use,
what its `__init__.py` holds, and the one direction its modules import in. Every rule names the file
of a consuming project it is verified against, the test that holds it and the probe a rule about a
tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of its PR 11,
whose contracts spec and that spec's revision record each choice as a Decision; the evidence is in
the `verification/` of the spec of issue #21 in `patchbay-standards` and of its revision after the
review of PR 25, patchbay's own probes cited by name and the ones those specs added by letter. The
toolchain spec of issue #4 deferred its `__init__.py` rules here.

Where a test file lives is `base/testing/tests.md`'s; how a name is re-exported so mypy sees it is
`base/python/typing.md`'s.

## The package

- **`src/<package>/` holds one module per concern.** patchbay's core holds four: `contracts.py`,
  the protocol an adapter implements; `models.py`, the values that cross a boundary; `events.py`,
  the events, their bus and its subscriptions; `errors.py`, the exceptions. Verified against
  `src/patchbay/` and the docstring of `src/patchbay/__init__.py`.
- **What a consumer's tests use is a `testing/` subpackage, shipped in the wheel**, a module per
  thing it holds: patchbay's `patchbay.testing` holds the contract tests (`contract_tests.py`),
  the reference implementation they are proven against (`fake.py`) and a subscriber that records
  what it receives (`recording.py`). The root does not re-export it and no module outside it
  imports it, so importing the package loads none of it; a consumer imports it by name. It imports
  no pytest (`base/testing/tests.md`). Verified against `src/patchbay/testing/`, its
  `__init__.py`'s docstring, `src/patchbay/__init__.py`, and the wheel's files and the modules an
  import of the package loads, in the `verification/patchbay-evidence.txt` of the spec of issue #21.
- **No two modules of the package share a basename**, its subpackages' included, so the test
  module each takes its name from (`base/testing/tests.md`, the mirror) is one no other test module
  has, and mypy, which reads `tests/` with no `__init__.py`, never meets two modules of one name.
  The named exception is `__init__.py`, one per package, whose tests take their names from what
  they hold (`base/testing/tests.md`). patchbay's seven, `contracts`, `errors`, `events`, `models`,
  `contract_tests`, `fake` and `recording`, are seven names. Verified against `src/patchbay/` and
  `tests/unit/`; probe n.

## `__init__.py`

- **A package's `__init__.py` holds its re-exports and `__all__`, the root's `__version__` too, and
  nothing else**: no definition and no logic. A module the root imports for itself is bound to a
  private name (`import importlib.metadata as _metadata`), so every public name the root binds is
  an export. `testing/__init__.py` holds re-exports and `__all__` alone. Verified against
  `src/patchbay/__init__.py`, `src/patchbay/testing/__init__.py` and `tests/unit/test_package.py`
  (`test_public_names_are_in_all`).
- **`__version__` is read from the installed distribution's metadata**,
  `importlib.metadata.version("<distribution>")`, so `pyproject.toml` is the one place the version
  is written. Nothing falls back around it: where no distribution is installed, as from a bare
  `src/` on `sys.path`, `importlib.metadata` raises `PackageNotFoundError` and the import fails,
  rather than the package inventing a version. Verified against `src/patchbay/__init__.py`, its
  docstring, and `tests/unit/test_version.py` (`test_version_matches_pyproject`).
- **A test holds the root's surface to `__all__`**: every name the root binds without a leading
  underscore is in `__all__`; every name in `__all__` is bound, and listed once; and each is the
  very object its module defines, not a copy or a second type. Submodules are left out of the
  first: importing `patchbay.errors` binds `errors` on the package, the import system's doing and
  not an export, and `from patchbay import *` does not import them. Verified against
  `tests/unit/test_package.py` (`test_public_names_are_in_all`, `test_every_name_in_all_resolves`,
  `test_the_package_re_exports_the_contract_surface`).

## One direction of import

- **The modules import in one direction, from the errors module up to the root, and are built in
  that order with the gate green after each.** The errors module is the leaf and imports nothing
  from its package (`base/python/errors.md`). In patchbay, `models.py` imports `errors.py`;
  `events.py` imports both; `contracts.py` imports `events.py` and `models.py`; the `testing`
  modules import those; `__init__.py` imports the four. They were built in that order, errors,
  models, events, contracts, the `testing` subpackage with the fake, the contract tests, then
  `__init__.py`, with the gate green after each, at 28, 103, 127, 131, 162, 186 and 188 tests: a
  module cannot pass mypy before what it imports exists. Verified against the imports of each
  module in `src/patchbay/` and the contracts spec's `shape.md` ("Results").
- **A protocol that a module's own API takes lives in that module, beside the API**, so no two
  modules import each other: `Subscriber` is defined in `events.py`, beside the
  `EventBus.subscribe` that takes it, and `contracts.py` re-exports it (`base/python/typing.md`,
  "Re-exports"). `Subscriber` is bounded by `Event`: placed in `contracts.py`, it would have
  `contracts.py` import `Event` from `events.py`, and `events.py` import `Subscriber` from
  `contracts.py` for `subscribe`. Verified against
  `src/patchbay/events.py`, `src/patchbay/contracts.py` and `tests/unit/test_contracts.py`
  (`test_subscriber_is_the_events_module_s_own`).

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/layout.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.
