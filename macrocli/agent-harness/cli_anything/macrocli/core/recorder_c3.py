# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403


class MacroRecorderMixin3:
    def interactive_agent_review(self, snapshots_dir: Optional[str] = None) -> None:
        """Interactively review all steps and mark some as agent steps.

        For each step the user can:
          - Press Enter → keep as fixed step
          - Type 'a'   → mark as agent step, then provide description,
                         end_state_description, and take a snapshot

        snapshots_dir: where to save end_state snapshots (default: output_dir/snapshots)
        """
        snap_dir = Path(snapshots_dir or self.output_dir / "snapshots")
        snap_dir.mkdir(parents=True, exist_ok=True)

        print()
        print("─" * 60)
        print("  Step Review — mark steps as 'fixed' or 'agent'")
        print("  Enter = fixed (fast, deterministic)")
        print("  a     = agent step (vision model decides at runtime)")
        print("─" * 60)

        for i, step in enumerate(self._steps):
            # Build a human-readable description of the step
            if step.kind == "click":
                step_desc = f"click {step.window_title or 'screen'} ({step.x_pct:.2f}, {step.y_pct:.2f})"
            elif step.kind == "type":
                preview = step.text[:40] + "..." if len(step.text) > 40 else step.text
                step_desc = f"type_text {preview!r}"
            elif step.kind == "hotkey":
                step_desc = f"hotkey {step.keys}"
            elif step.kind == "scroll":
                step_desc = f"scroll dy={step.dy}"
            else:
                step_desc = step.kind

            print(f"\n  [{i + 1}/{len(self._steps)}] {step_desc}")

            try:
                choice = (
                    input("  → fixed or agent? [Enter=fixed / a=agent]: ")
                    .strip()
                    .lower()
                )
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if choice != "a":
                continue

            # Mark as agent step
            step.is_agent_step = True

            try:
                step.agent_description = input(
                    "  → Describe what this step needs to do:\n    "
                ).strip()
                step.agent_end_state_description = input(
                    "  → Describe the target end state (what should the screen show):\n    "
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            # Capture end-state snapshot
            print("  → Now manually operate the UI to reach the end state.")
            try:
                input("    Press Enter when ready to take snapshot...")
            except (EOFError, KeyboardInterrupt):
                print()
                continue

            snapshot_path = str(snap_dir / f"step_{step.index:03d}_end_state.png")
            if self._capture_end_state_snapshot(snapshot_path):
                step.agent_end_state_snapshot = snapshot_path
                print(f"  ✓ Snapshot saved: {snapshot_path}")
            else:
                print("  ⚠ Snapshot failed — no snapshot will be used for this step.")

        print()
        print("─" * 60)
        agent_count = sum(1 for s in self._steps if s.is_agent_step)
        fixed_count = len(self._steps) - agent_count
        print(f"  Review complete: {fixed_count} fixed, {agent_count} agent steps")
        print("─" * 60)

    def _capture_end_state_snapshot(self, output_path: str) -> bool:
        """Capture the current screen and save as end-state snapshot."""
        try:
            import mss
            from PIL import Image

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                raw = sct.grab(monitor)
                img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
                img.save(output_path)
            return True
        except Exception as e:
            print(f"[recorder] Snapshot failed: {e}", file=sys.stderr)
            return False

    def get_type_steps(self) -> list[tuple[int, "RecordedStep"]]:
        """Return (list_index, step) for every non-empty type_text step."""
        return [
            (i, s)
            for i, s in enumerate(self._steps)
            if s.kind == "type" and s.text.strip()
        ]
