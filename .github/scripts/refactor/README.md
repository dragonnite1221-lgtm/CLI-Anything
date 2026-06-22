# Behavior-preserving refactor tools (200-line gate burndown)

AST-based utilities to split oversized Python modules under the 200-line gate
without changing behavior. Run each behind a test/AST gate that reverts on
regression — never blindly.

- `extract_block.py` — extract a statement block into a helper via precise data-flow
  (inputs/outputs computed with liveness; loop/comprehension targets excluded).
- `extract_if_body.py` — extract an always-returning if-branch into `return _handler(...)`.
- `auto_decompose.py` — repeatedly extract from every giant function until each fits.
- `split_pkg.py` — split top-level items into `_base` + `_pN` + façade (relative, cross-imports).
- `split_pkgclass.py` — split a giant class into method mixins (test-aware naming).
- `split_testpkg.py` — split a pytest module's classes into underscore parts + façade.
- `split_collection.py` — split a giant List/Dict literal (any depth); verified identical.
- `split_fstring.py` — split a giant f-string into helper slices.
- `reexport_pkg.py` — rewrite a façade to re-export its parts' public surface.

## Import-cycle tooling

- `cycle_fix.py <pkgdir>` — report top-level cross-part import back-edges (cycle closers).
- `break_cycle.py <pkgdir>` — break cycles by deferring the runtime-only import below
  the hub's definitions (skips symbols used as decorators / at module level).

Pair with `.github/scripts/check_imports.py` (the import-integrity gate) which imports
every package and fails on structural errors (cycles, dropped re-exports) the
line-count gate cannot see.
