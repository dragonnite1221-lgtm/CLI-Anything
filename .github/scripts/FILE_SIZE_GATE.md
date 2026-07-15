# 200-line Python file-size gate

All tracked Python files must be **≤ 200 lines**. Existing oversized files are
frozen in `.github/scripts/file_size_baseline.txt`; no *new* violation, baseline
growth, or stale baseline entry is allowed. The baseline is burned down over
time by behavior-preserving splits.

The gate lives under `.github/scripts/` (not root `scripts/`) because this
repo's `.gitignore` ignores everything at the root except an explicit
allow-list — `.github/` is one of the tracked areas.

## Run the gate

```bash
python .github/scripts/check_file_size.py            # check (exit 1 on new/grown violations)
python .github/scripts/check_file_size.py --write-baseline   # regenerate after a split
```

## Enforcement

- **CI**: `.github/workflows/file-size.yml` runs the gate on push/PR (when
  GitHub Actions minutes are available).
- **Local pre-push hook** (recommended while CI is unavailable) — enable once:

  ```bash
  git config core.hooksPath .github/hooks
  ```

  After that, `git push` runs `.github/hooks/pre-push`, which executes the gate
  and blocks the push on a new or grown violation.

## Regenerating the baseline

Only regenerate after you have genuinely **shrunk** files (a split that removes
a violation). Never regenerate to paper over a new violation — that defeats the
gate. Commit the regenerated `file_size_baseline.txt` with the split that
caused it.
