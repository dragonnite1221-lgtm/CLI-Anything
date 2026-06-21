# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin6:
    def _to_dap_breakpoint(
        self,
        payload: dict[str, Any],
        source_path: str | None = None,
        requested_line: int | None = None,
    ) -> dict[str, Any]:
        details = payload.get("location_details") or []
        first = details[0] if details else {}
        path = first.get("file") or source_path
        line = first.get("line") or requested_line or 0
        dap_bp = {
            "id": payload.get("id"),
            "verified": bool(payload.get("resolved")),
            "line": line,
        }
        if path:
            dap_bp["source"] = self._source_from_path(path)
        if first.get("address"):
            dap_bp["instructionReference"] = first["address"]
        if not dap_bp["verified"]:
            dap_bp["message"] = (
                "Breakpoint is pending and has no resolved LLDB locations yet."
            )
        return dap_bp

    def _source_from_path(self, path: str | None) -> dict[str, Any] | None:
        if not path:
            return None
        source_path = str(path)
        return {"name": Path(source_path).name, "path": source_path}

    def _ensure_session(self) -> LLDBSession:
        if self._session is None:
            self._session = self._session_factory()
        return self._session

    def _alloc_frame_ref(self, thread_id: int, frame_index: int) -> int:
        ref = self._next_ref
        self._next_ref += 1
        self._frame_refs[ref] = (thread_id, frame_index)
        return ref

    def _alloc_variable_ref(self, entry: dict[str, Any]) -> int:
        ref = self._next_ref
        self._next_ref += 1
        self._variable_refs[ref] = entry
        return ref

    def _dap_variables_from_values(self, values) -> list[dict[str, Any]]:
        return [
            self._dap_variable_from_value(value)
            for value in values
            if value and value.IsValid()
        ]

    def _dap_variable_from_value(self, value) -> dict[str, Any]:
        variables_ref = 0
        if value.GetNumChildren() > 0:
            variables_ref = self._alloc_variable_ref(
                {"kind": "children", "value": value}
            )
        payload = {
            "name": value.GetName() or "<unnamed>",
            "value": self._value_display(value),
            "type": value.GetTypeName(),
            "variablesReference": variables_ref,
        }
        evaluate_name = self._value_expression_path(value)
        if evaluate_name:
            payload["evaluateName"] = evaluate_name
        return payload

    def _child_values(self, value) -> list[Any]:
        return [value.GetChildAtIndex(index) for index in range(value.GetNumChildren())]

    def _value_display(self, value) -> str:
        raw = value.GetValue()
        summary = value.GetSummary()
        if raw and summary:
            return f"{raw} {summary}"
        return raw or summary or ""

    def _value_expression_path(self, value) -> str | None:
        try:
            stream = self._ensure_session()._lldb.SBStream()
            value.GetExpressionPath(stream)
            text = stream.GetData()
            return text or value.GetName()
        except Exception:
            return value.GetName()

    def _reset_refs_for_resume(self):
        self._frame_refs.clear()
        self._variable_refs.clear()

    def _coerce_args(self, raw: Any) -> list[str] | None:
        if raw is None:
            return None
        if isinstance(raw, str):
            return shlex.split(raw, posix=os.name != "nt")
        return [str(item) for item in raw]

    def _coerce_env(self, raw: Any) -> list[str] | None:
        if raw is None:
            return None
        if isinstance(raw, dict):
            return [f"{key}={value}" for key, value in raw.items()]
        return [str(item) for item in raw]

    def _parse_address(self, value: str) -> int:
        return int(value, 0)
