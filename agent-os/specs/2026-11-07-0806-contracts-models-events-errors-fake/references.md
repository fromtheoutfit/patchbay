# References for contracts, models, errors, events and FakeInstrument (issue #10)

The first code in core: there is no prior implementation of a contract, model, error or event to
borrow from. The owner named the existing Python as the reference for its form (Step 3).

## Similar Implementations

### The package's surface

- **Location:** `src/patchbay/__init__.py`
- **Relevance:** the one module the package had. Its docstring says what the package exports and
  why, and `__all__` is the surface; `implicit_reexport = false` in `[tool.mypy]` holds a name to
  `__all__` or an explicit `from x import y as y`.
- **Key patterns:** a module docstring that says what the module is for and what it is not; a
  private alias for an import the package does not mean to export (`_metadata`); `__all__` the
  whole surface. Every new module and `testing/__init__.py` take the same form.

### The version test and its properties

- **Location:** `tests/unit/test_version.py`
- **Relevance:** the one hypothesis test in the tree.
- **Key patterns:** one docstring per test saying the property it holds; `@given` with a strategy
  narrowed to the case, `@example` for the case a strategy would rarely draw, tried on every run;
  a module-level constant with a comment saying why it is what it is; `pytestconfig` for paths.

### The package's metadata test

- **Location:** `tests/unit/test_package.py`
- **Relevance:** holds every public name the package binds to `__all__`; this spec's
  re-exports must keep it passing, and it gains a check that every name in `__all__` resolves.
- **Key patterns:** a test of the surface, not of behaviour; read from the installed package.
