# ruff: noqa: F403, F405, E501
from .recorder_base import *  # noqa: F403


class MacroRecorderMixin1:
    def on_scroll(self, x: int, y: int, dx: int, dy: int):
        with self._lock:
            self._flush_pending_chars()
            idx = self._next_index()
            # Capture template near scroll position
            template_file = str(self.templates_dir / f"step_{idx:03d}_scroll.png")
            captured = _capture_template(x, y, template_file)

            step = RecordedStep(
                index=idx,
                kind="scroll",
                x=x,
                y=y,
                dx=dx,
                dy=dy,
                template_path=template_file if captured else "",
            )
            self._steps.append(step)

    def on_key_press(self, key):
        key_str = _key_to_str(key)

        # Check stop hotkey
        if key_str.lower() in ("ctrl", "alt"):
            self._pressed_modifiers.add(key_str.lower())
        elif key_str.lower() == "s" and self._pressed_modifiers >= {"ctrl", "alt"}:
            print(
                "\n[recorder] Stop hotkey detected (Ctrl+Alt+S). Stopping...",
                flush=True,
            )
            self._stop_event.set()
            return False  # stop listener

        if (
            key_str in _MODIFIER_KEYS
            or _KEY_NAME_MAP.get(key_str, key_str) in _MODIFIER_KEYS
        ):
            self._pressed_modifiers.add(_KEY_NAME_MAP.get(key_str, key_str))
            return

        # If modifiers are pressed, it's a hotkey combination
        # But only if the key itself is NOT a modifier
        normalized_key = _KEY_NAME_MAP.get(key_str, key_str)
        is_modifier = normalized_key in {"ctrl", "shift", "alt", "cmd", "super"}
        active_mods = {_KEY_NAME_MAP.get(m, m) for m in self._pressed_modifiers}

        if active_mods and not is_modifier:
            with self._lock:
                self._flush_pending_chars()
                combo = "+".join(sorted(active_mods) + [key_str])
                idx = self._next_index()
                step = RecordedStep(index=idx, kind="hotkey", keys=combo)
                self._steps.append(step)
                print(f"[recorder] hotkey #{idx}: {combo}", flush=True)
        elif not is_modifier:
            # Regular character or special key
            # space key comes as Key.space (len > 1), treat as printable
            is_space = key_str == "space"
            if len(key_str) == 1 or is_space:
                char = " " if is_space else key_str
                with self._lock:
                    self._pending_chars.append(char)
            else:
                # Special key alone (enter, tab, backspace, etc.)
                with self._lock:
                    self._flush_pending_chars()
                    idx = self._next_index()
                    step = RecordedStep(index=idx, kind="hotkey", keys=key_str)
                    self._steps.append(step)

    def on_key_release(self, key):
        key_str = _key_to_str(key)
        normalized = _KEY_NAME_MAP.get(key_str, key_str)
        self._pressed_modifiers.discard(normalized)

    def record(self, timeout_s: Optional[float] = None) -> list[RecordedStep]:
        """Start recording. Blocks until Ctrl+Alt+S or timeout_s seconds."""
        try:
            from pynput import mouse as mouse_mod, keyboard as kb_mod
        except ImportError:
            raise ImportError("pynput is required for recording.\n  pip install pynput")

        self.templates_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"[recorder] Recording '{self.macro_name}'. Press Ctrl+Alt+S to stop.",
            flush=True,
        )

        mouse_listener = mouse_mod.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll,
        )
        kb_listener = kb_mod.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release,
        )

        mouse_listener.start()
        kb_listener.start()

        try:
            self._stop_event.wait(timeout=timeout_s)
        except KeyboardInterrupt:
            pass
        finally:
            mouse_listener.stop()
            kb_listener.stop()

        with self._lock:
            self._flush_pending_chars()

        print(f"[recorder] Recorded {len(self._steps)} steps.", flush=True)
        return self._steps
