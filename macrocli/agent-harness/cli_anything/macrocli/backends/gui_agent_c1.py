# ruff: noqa: F403, F405, E501
from .gui_agent_base import *  # noqa: F403


class GUIAgentBackendMixin1:
    def _instruct(
        self, p: dict, context: BackendContext, t0: float
    ) -> StepResult:
        """Execute exactly ONE action decided by the vision model.

        The macro author is responsible for:
        - focusing the target window before calling gui_agent
        - writing multiple gui_agent steps if multiple actions are needed
        - verifying the outcome via postconditions or subsequent steps

        This step:
          1. Takes a screenshot
          2. Sends it + description + end_state_snapshot to the model
          3. Model returns one action (click/type/hotkey/scroll/done)
          4. Executes that action
          5. Returns success with the action taken
        """
        description: str = p.get("description", "")
        end_state_desc: str = p.get("end_state_description", "")
        snapshot_path: str = p.get("end_state_snapshot", "")
        window_title: str = p.get("window_title", "")  # focus this window first
        model_name: str = p.get("model", os.environ.get("MACROCLI_MODEL", ""))
        api_key: str = p.get("api_key", os.environ.get("MACROCLI_API_KEY", ""))
        base_url: str = p.get("base_url", os.environ.get("MACROCLI_BASE_URL", ""))

        if not model_name:
            return StepResult(
                success=False,
                error="GUIAgentBackend: model required. Set MACROCLI_MODEL env var or pass model in step params.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        if not api_key:
            return StepResult(
                success=False,
                error="GUIAgentBackend: api_key required. Set MACROCLI_API_KEY env var.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            from openai import OpenAI
        except ImportError:
            return StepResult(
                success=False,
                error="openai required: pip install openai",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = OpenAI(**client_kwargs)

        def _call_model(messages: list, max_tokens: int = 1024) -> str:
            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()

        def _extract_json(raw: str) -> dict:
            """Extract JSON from model output robustly."""
            if raw.startswith("```"):
                raw = "\n".join(
                    l for l in raw.split("\n") if not l.startswith("```")
                ).strip()
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1:
                raw = raw[start:end+1]
            return json.loads(raw)

        # Step 1: Focus the target window if specified
        if window_title and not context.dry_run:
            import shutil, subprocess
            env = os.environ.copy()
            if "DISPLAY" not in env:
                env["DISPLAY"] = ":0"
            if shutil.which("wmctrl"):
                subprocess.run(["wmctrl", "-a", window_title],
                               capture_output=True, env=env)
            elif shutil.which("xdotool"):
                subprocess.run(
                    ["xdotool", "search", "--name", window_title,
                     "windowfocus", "--sync"],
                    capture_output=True, env=env
                )
            time.sleep(0.3)

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "description": description},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        # Step 2: Take screenshot
        current_b64 = _screenshot_b64()

        # Step 3: Load end state snapshot if provided
        end_state_b64: Optional[str] = None
        if snapshot_path and Path(snapshot_path).is_file():
            end_state_b64 = _file_to_b64(snapshot_path)

        # Step 4: Build prompt
        content = []
        content.append({"type": "text", "text": "CURRENT SCREEN STATE:"})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{current_b64}"}
        })
        if end_state_b64:
            content.append({"type": "text", "text": "TARGET END STATE:"})
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{end_state_b64}"}
            })
        task_text = f"TASK: {description}"
        if end_state_desc:
            task_text += f"\nTARGET: {end_state_desc}"
        task_text += "\nOutput ONE action as JSON only."
        content.append({"type": "text", "text": task_text})

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]

        # Step 5: Ask model for one action
        try:
            raw = _call_model(messages)
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"GUIAgentBackend: model error: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            action_dict = _extract_json(raw)
        except json.JSONDecodeError:
            return StepResult(
                success=False,
                error=f"GUIAgentBackend: invalid JSON from model: {raw[:200]}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        action_name = action_dict.get("action", "")
        print(f"[gui_agent] action: {action_dict}", flush=True)

        # Step 6: Execute the action (unless model says done)
        if action_name != "done":
            try:
                _execute_action(action_dict, context)
            except Exception as exc:
                return StepResult(
                    success=False,
                    error=f"GUIAgentBackend: action execution failed: {exc}",
                    backend_used=self.name,
                    duration_ms=(time.time() - t0) * 1000,
                )
            time.sleep(0.5)

        return StepResult(
            success=True,
            output={
                "action": action_dict,
                "done": action_name == "done",
            },
            backend_used=self.name,
            duration_ms=(time.time() - t0) * 1000,
        )
