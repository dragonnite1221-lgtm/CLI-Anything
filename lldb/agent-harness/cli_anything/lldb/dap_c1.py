# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin1:
    def _handle_attach(self, args: dict[str, Any]):
        program = _first_present(args, "program", "executable")
        pid = _first_present(args, "pid", "processId")
        name = _first_present(args, "name", "processName")
        if pid is None and not name:
            raise RuntimeError("attach requires pid/processId or name/processName")
        if program:
            self._ensure_session().target_create(str(program), arch=args.get("arch"))
        else:
            self._ensure_session().target_create_empty(arch=args.get("arch"))
        self._pending_attach = {
            "pid": int(pid) if pid is not None else None,
            "name": str(name) if name else None,
            "wait_for": bool(args.get("waitFor", False)),
        }
        self._configure_stop_rules(args)
        self._pending_launch = None
        return {}, None

    def _handle_configurationDone(self, _args: dict[str, Any]):
        def post_send():
            default_reason = None
            if self._pending_launch is not None:
                launch_args = self._pending_launch
                self._pending_launch = None
                self._ensure_session().launch(**launch_args)
                self._emit_breakpoint_updates()
                default_reason = (
                    "entry" if launch_args.get("stop_at_entry") else "breakpoint"
                )
            elif self._pending_attach is not None:
                attach_args = self._pending_attach
                self._pending_attach = None
                if attach_args["pid"] is not None:
                    self._ensure_session().attach_pid(attach_args["pid"])
                else:
                    self._ensure_session().attach_name(
                        attach_args["name"], wait_for=attach_args["wait_for"]
                    )
                default_reason = "pause"
            self._emit_execution_event(default_reason=default_reason)

        return {}, post_send

    def _handle_disconnect(self, args: dict[str, Any]):
        terminate_debuggee = bool(args.get("terminateDebuggee", True))

        def post_send():
            if self._session is not None:
                if (
                    not terminate_debuggee
                    and self._session.session_status().get("process_origin")
                    == "launched"
                ):
                    try:
                        self._session.detach()
                    except Exception:
                        pass
                self._session.destroy()
                self._session = None
            self._send_event("terminated")

        return {}, post_send

    def _handle_setBreakpoints(self, args: dict[str, Any]):
        source = args.get("source") or {}
        path = source.get("path")
        if not path:
            raise RuntimeError("setBreakpoints requires source.path")

        self._ensure_stopped_for_target_mutation("setBreakpoints")
        session = self._ensure_session()
        source_key = str(Path(path))
        with self._lldb_api_lock:
            for bp_id in self._source_breakpoints.get(source_key, []):
                try:
                    session.breakpoint_delete(bp_id)
                except Exception:
                    pass

            dap_breakpoints = []
            created_ids = []
            for item in args.get("breakpoints") or []:
                line = int(item.get("line"))
                payload = session.breakpoint_set(
                    file=source_key,
                    line=line,
                    condition=item.get("condition"),
                    allow_pending=True,
                )
                created_ids.append(payload["id"])
                dap_breakpoints.append(
                    self._to_dap_breakpoint(payload, source_key, requested_line=line)
                )

        self._source_breakpoints[source_key] = created_ids
        return {"breakpoints": dap_breakpoints}, None

    def _handle_setFunctionBreakpoints(self, args: dict[str, Any]):
        self._ensure_stopped_for_target_mutation("setFunctionBreakpoints")
        session = self._ensure_session()
        with self._lldb_api_lock:
            for bp_id in self._function_breakpoints:
                try:
                    session.breakpoint_delete(bp_id)
                except Exception:
                    pass

            self._function_breakpoints = []
            result = []
            for item in args.get("breakpoints") or []:
                name = item.get("name")
                if not name:
                    continue
                payload = session.breakpoint_set(
                    function=str(name),
                    condition=item.get("condition"),
                    allow_pending=True,
                )
                self._function_breakpoints.append(payload["id"])
                result.append(self._to_dap_breakpoint(payload))
        return {"breakpoints": result}, None
