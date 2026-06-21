# ruff: noqa: F403, F405, E501
from .gui_agent_base import *  # noqa: F403


class GUIAgentBackendMixin2:
    def _instruct_with_refine(
        self, p: dict, context: BackendContext, t0: float
    ) -> StepResult:
        """Execute one action, then compare result vs end_state_snapshot,
        and if needed undo and re-execute with a refined action.

        Sends to model on refine:
          - Screenshot BEFORE first action (original state)
          - The first action that was taken
          - Screenshot AFTER first action (current result)
          - end_state_snapshot (target state)
          - Request for corrected action

        This allows the model to see exactly what went wrong and correct it.
        """
        snapshot_path: str = p.get("end_state_snapshot", "")

        if not snapshot_path or not Path(snapshot_path).is_file():
            # No end state snapshot → fall back to single instruct
            return self._instruct(p, context, t0)

        # ── Round 1: initial action ───────────────────────────────────────────
        before_b64 = _screenshot_b64()
        result1 = self._instruct(p, context, t0)

        if not result1.success:
            return result1

        first_action = result1.output.get("action", {})
        if first_action.get("action") == "done":
            return result1

        time.sleep(0.5)
        after_b64 = _screenshot_b64()
        end_state_b64 = _file_to_b64(snapshot_path)

        # ── Round 2: compare and refine ───────────────────────────────────────
        description: str = p.get("description", "")
        end_state_desc: str = p.get("end_state_description", "")
        model_name: str = p.get("model", os.environ.get("MACROCLI_MODEL", ""))
        api_key: str = p.get("api_key", os.environ.get("MACROCLI_API_KEY", ""))
        base_url: str = p.get("base_url", os.environ.get("MACROCLI_BASE_URL", ""))

        from openai import OpenAI
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)

        def _call(messages):
            resp = client.chat.completions.create(
                model=model_name, messages=messages, max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()

        def _extract_json(raw):
            if raw.startswith("```"):
                raw = "\n".join(l for l in raw.split("\n") if not l.startswith("```")).strip()
            s, e = raw.find('{'), raw.rfind('}')
            if s != -1 and e != -1:
                raw = raw[s:e+1]
            return json.loads(raw)

        refine_prompt = f"""You are refining a GUI automation action.

ORIGINAL TASK: {description}
TARGET STATE: {end_state_desc}

WHAT HAPPENED:
- First action taken: {json.dumps(first_action)}

Now compare these three screenshots:

1. BEFORE (original state before any action):
2. AFTER FIRST ACTION (current result):
3. TARGET END STATE (what it should look like):

The first action was not quite right. Looking at:
- Where the rectangle was drawn vs where it should be
- The difference between AFTER and TARGET

Provide a corrected drag action with better coordinates.
Output ONE JSON action only."""

        content = [
            {"type": "text", "text": refine_prompt},
            {"type": "text", "text": "BEFORE:"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{before_b64}"}},
            {"type": "text", "text": "AFTER FIRST ACTION:"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{after_b64}"}},
            {"type": "text", "text": "TARGET END STATE:"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{end_state_b64}"}},
        ]

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]

        try:
            raw = _call(messages)
            refined_action = _extract_json(raw)
            print(f"[gui_agent] refined action: {refined_action}", flush=True)
        except Exception as exc:
            # Refine failed, return original result
            print(f"[gui_agent] refine failed: {exc}, keeping original", flush=True)
            return result1

        if refined_action.get("action") == "done":
            return result1

        # Undo the first action, then execute the refined one
        import shutil, subprocess as sp
        env = os.environ.copy()
        if "DISPLAY" not in env:
            env["DISPLAY"] = ":0"
        if shutil.which("xdotool"):
            sp.run(["xdotool", "key", "ctrl+z"], env=env)
            time.sleep(0.3)

        try:
            _execute_action(refined_action, context)
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"GUIAgentBackend: refine action failed: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        time.sleep(0.5)

        return StepResult(
            success=True,
            output={
                "action": refined_action,
                "first_action": first_action,
                "refined": True,
                "done": False,
            },
            backend_used=self.name,
            duration_ms=(time.time() - t0) * 1000,
        )
