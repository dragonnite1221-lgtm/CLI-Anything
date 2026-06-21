# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin5:
    def _emit_execution_event(self, default_reason: str | None = None):
        info = self._ensure_session().process_info()
        state = info.get("state")
        if state in {"running", "launching", "stepping"}:
            self._send_continued_event(info.get("selected_thread_id"))
            return
        if state == "exited":
            self._send_event("exited", {"exitCode": info.get("exit_status", 0) or 0})
            self._send_event("terminated")
            return
        if state == "detached":
            self._send_event("terminated")
            return

        stop = info.get("stop") or {}
        lldb_reason = stop.get("reason")
        reason = (
            "entry"
            if default_reason == "entry"
            else (lldb_reason or default_reason or "pause")
        )
        if reason in {"signal", "crashed"}:
            reason = "exception"
        stop_origin = "debuggee"
        if self._pause_requested:
            self._pause_requested = False
            reason = "pause"
            stop_origin = "manualPause"

        frame = stop.get("frame") if isinstance(stop.get("frame"), dict) else {}
        stop_context = {
            "reason": reason,
            "lldbReason": lldb_reason,
            "description": stop.get("description"),
            "module": stop.get("module") or frame.get("module"),
            "modulePath": frame.get("module_path"),
            "function": stop.get("function") or frame.get("function"),
            "frame": frame,
        }
        matched_rule = (
            None
            if stop_origin == "manualPause"
            else self._match_stop_rule(stop_context)
        )
        if matched_rule is not None:
            stop_origin = matched_rule.origin

        body = {
            "reason": reason,
            "threadId": info.get("selected_thread_id"),
            "allThreadsStopped": True,
            "cliAnythingStop": {
                "origin": stop_origin,
                "lldbReason": lldb_reason,
                "module": stop_context["module"],
                "modulePath": stop_context["modulePath"],
                "function": stop_context["function"],
                "description": stop_context["description"],
            },
        }
        if frame:
            body["cliAnythingStop"]["frame"] = frame
        if matched_rule is not None:
            body["cliAnythingStop"]["matchedRule"] = matched_rule.to_dap()
        hit_ids = stop.get("hit_breakpoint_ids") or []
        if hit_ids:
            body["hitBreakpointIds"] = hit_ids
        if stop.get("description"):
            body["description"] = stop["description"]
            body["text"] = stop["description"]
        if matched_rule is not None and matched_rule.action == "continue":
            self._send_event(
                "output",
                {
                    "category": "console",
                    "output": (
                        f"auto-continued stop rule {matched_rule.name}: "
                        f"{self._summarize_stop(body)}\n"
                    ),
                },
            )
            self._send_continued_event(info.get("selected_thread_id"))
            self._start_continue_thread(
                name="cli-anything-lldb-dap-auto-continue",
                default_reason=default_reason or "breakpoint",
            )
            return
        self._send_event("stopped", body)

    def _match_stop_rule(self, stop_context: dict[str, Any]) -> StopRule | None:
        for rule in self._active_stop_rules:
            if rule.matches(stop_context):
                return rule
        return None

    def _summarize_stop(self, body: dict[str, Any]) -> str:
        text = str(
            body.get("description")
            or body.get("text")
            or body.get("reason")
            or "unknown"
        )
        return text.splitlines()[0] if text else "unknown"

    def _send_continued_event(self, thread_id: int | None = None):
        body: dict[str, Any] = {"allThreadsContinued": True}
        if thread_id is not None:
            body["threadId"] = thread_id
        self._send_event("continued", body)

    def _cleanup_session(self):
        if self._session is not None:
            try:
                self._session.destroy()
            finally:
                self._session = None

    def _emit_breakpoint_updates(self):
        for bp in self._ensure_session().breakpoint_list().get("breakpoints", []):
            self._send_event(
                "breakpoint",
                {"reason": "changed", "breakpoint": self._to_dap_breakpoint(bp)},
            )
