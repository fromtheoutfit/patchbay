# Mission

patchbay is headless control of software instruments from Python. This repository is core: the
contracts an instrument adapter implements, the host that loads adapters and drives them, and the
CLI that exposes the host. An adapter is its own package, `patchbay-<instrument>`, and plugs into
these.

## What core is

- The contracts: what every adapter promises, so a script written against one instrument reads
  the same against the next.
- The host: discovers adapters, opens an instrument, routes a call to it, closes it.
- The CLI: the host from a shell, for a person or a script.

## What core is not

- No synth-specific concept lives here. A parameter page, a voice mode, a preset bank format
  belong to the adapter that has them.
- Core grows only when a second adapter needs the same thing. One adapter wanting something is
  that adapter's; two is a contract.
- Not a product. An experiment in controlling instruments without their screens, kept honest by
  the gate and the standards.
