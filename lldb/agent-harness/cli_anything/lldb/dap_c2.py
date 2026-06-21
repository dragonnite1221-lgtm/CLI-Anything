# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin2:
    def _handle_threads(self, _args: dict[str, Any]):
        threads = []
        for item in self._ensure_session().threads().get("threads", []):
            name = item.get("name") or f"Thread {item.get('id')}"
            threads.append({"id": item["id"], "name": name})
        return {"threads": threads}, None

    def _handle_stackTrace(self, args: dict[str, Any]):
        thread_id = int(args.get("threadId"))
        start = int(args.get("startFrame", 0))
        levels = int(args.get("levels", 50) or 50)
        session = self._ensure_session()
        session.thread_select(thread_id)
        backtrace = session.backtrace(limit=start + levels)
        frames = []
        for frame in backtrace.get("frames", [])[start : start + levels]:
            frame_id = self._alloc_frame_ref(thread_id, int(frame["index"]))
            source = self._source_from_path(frame.get("file"))
            frames.append(
                {
                    "id": frame_id,
                    "name": frame.get("function") or "<unknown>",
                    "source": source,
                    "line": frame.get("line") or 0,
                    "column": 0,
                    "instructionPointerReference": frame.get("address"),
                }
            )
        return {
            "stackFrames": frames,
            "totalFrames": backtrace.get("total_frames", len(frames)),
        }, None

    def _handle_scopes(self, args: dict[str, Any]):
        frame_id = int(args.get("frameId"))
        if frame_id not in self._frame_refs:
            raise RuntimeError(f"Unknown frameId: {frame_id}")
        ref = self._alloc_variable_ref({"kind": "locals", "frame_ref": frame_id})
        return {
            "scopes": [
                {"name": "Locals", "variablesReference": ref, "expensive": False}
            ]
        }, None

    def _handle_variables(self, args: dict[str, Any]):
        ref = int(args.get("variablesReference"))
        entry = self._variable_refs.get(ref)
        if not entry:
            return {"variables": []}, None
        if entry["kind"] != "locals":
            if entry["kind"] == "children":
                return {
                    "variables": self._dap_variables_from_values(
                        self._child_values(entry["value"])
                    )
                }, None
            return {"variables": []}, None

        thread_id, frame_index = self._frame_refs[entry["frame_ref"]]
        session = self._ensure_session()
        session.thread_select(thread_id)
        session.frame_select(frame_index)
        return {
            "variables": self._dap_variables_from_values(session.local_values())
        }, None

    def _handle_setVariable(self, args: dict[str, Any]):
        ref = int(args.get("variablesReference"))
        name = str(args.get("name") or "")
        value = str(args.get("value") or "")
        entry = self._variable_refs.get(ref)
        if not entry:
            raise RuntimeError(f"Unknown variablesReference: {ref}")

        if entry["kind"] == "locals":
            thread_id, frame_index = self._frame_refs[entry["frame_ref"]]
            updated = self._ensure_session().set_local_variable(
                thread_id, frame_index, name, value
            )
        elif entry["kind"] == "children":
            updated = self._ensure_session().set_child_value(
                entry["value"], name, value
            )
        else:
            raise RuntimeError(
                f"Cannot set variable for reference kind: {entry['kind']}"
            )

        return self._dap_variable_from_value(updated), None

    def _handle_evaluate(self, args: dict[str, Any]):
        expression = args.get("expression")
        if not expression:
            raise RuntimeError("evaluate requires expression")
        frame_id = args.get("frameId")
        if frame_id is not None and int(frame_id) in self._frame_refs:
            thread_id, frame_index = self._frame_refs[int(frame_id)]
            self._ensure_session().thread_select(thread_id)
            self._ensure_session().frame_select(frame_index)
        payload = self._ensure_session().evaluate(str(expression))
        if payload.get("error"):
            raise RuntimeError(payload["error"])
        result = payload.get("value") or payload.get("summary") or ""
        return {
            "result": result,
            "type": payload.get("type"),
            "variablesReference": 0,
        }, None

    def _handle_continue(self, _args: dict[str, Any]):
        def post_send():
            self._reset_refs_for_resume()
            self._send_continued_event()
            self._start_continue_thread(
                name="cli-anything-lldb-dap-continue",
                default_reason="breakpoint",
            )

        return {"allThreadsContinued": True}, post_send

    def _handle_pause(self, _args: dict[str, Any]):
        def post_send():
            self._pause_requested = True
            self._request_async_interrupt()
            if not self._is_continue_active():
                with self._lldb_api_lock:
                    self._emit_execution_event(default_reason="pause")

        return {}, post_send

    def _handle_next(self, _args: dict[str, Any]):
        return {}, self._step_post_send(self._ensure_session().step_over)

    def _handle_stepIn(self, _args: dict[str, Any]):
        return {}, self._step_post_send(self._ensure_session().step_into)

    def _handle_stepOut(self, _args: dict[str, Any]):
        return {}, self._step_post_send(self._ensure_session().step_out)
