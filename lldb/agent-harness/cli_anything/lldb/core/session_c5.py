# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin5:
    def _breakpoint_payload(self, bp) -> Dict[str, Any]:
        locations = self._breakpoint_locations(bp)
        return {
            "id": bp.GetID(),
            "hits": bp.GetHitCount(),
            "locations": len(locations),
            "resolved": len(locations) > 0,
            "location_details": locations,
            "enabled": bp.IsEnabled(),
            "condition": bp.GetCondition() or None,
        }

    def _breakpoint_locations(self, bp) -> List[Dict[str, Any]]:
        result = []
        for i in range(bp.GetNumLocations()):
            loc = bp.GetLocationAtIndex(i)
            address = loc.GetAddress()
            line_entry = address.GetLineEntry()
            load_addr = address.GetLoadAddress(self.target)
            function = address.GetFunction()
            result.append(
                {
                    "id": loc.GetID(),
                    "address": hex(load_addr)
                    if load_addr != self._lldb.LLDB_INVALID_ADDRESS
                    else None,
                    "file": str(line_entry.GetFileSpec())
                    if line_entry.IsValid()
                    else None,
                    "line": line_entry.GetLine() if line_entry.IsValid() else None,
                    "column": line_entry.GetColumn() if line_entry.IsValid() else None,
                    "function": function.GetName()
                    if function and function.IsValid()
                    else None,
                    "enabled": loc.IsEnabled(),
                    "hit_count": loc.GetHitCount(),
                }
            )
        return result

    def _stop_info(self, thread) -> Dict[str, Any]:
        if thread is None or not thread.IsValid():
            return {
                "reason": None,
                "description": None,
                "hit_breakpoint_ids": [],
                "frame": None,
            }

        reason = thread.GetStopReason()
        reason_name = self._stop_reason_name(reason)
        frame = self._thread_frame_summary(thread)
        return {
            "reason": reason_name,
            "description": self._thread_stop_description(thread),
            "hit_breakpoint_ids": self._hit_breakpoint_ids(thread)
            if reason_name == "breakpoint"
            else [],
            "frame": frame,
            "module": frame.get("module") if frame else None,
            "function": frame.get("function") if frame else None,
        }

    def _stop_reason_name(self, reason: int) -> str | None:
        lldb = self._lldb
        mapping = {
            getattr(lldb, "eStopReasonBreakpoint", object()): "breakpoint",
            getattr(lldb, "eStopReasonWatchpoint", object()): "watchpoint",
            getattr(lldb, "eStopReasonSignal", object()): "signal",
            getattr(lldb, "eStopReasonException", object()): "exception",
            getattr(lldb, "eStopReasonTrace", object()): "step",
            getattr(lldb, "eStopReasonPlanComplete", object()): "step",
            getattr(lldb, "eStopReasonExec", object()): "entry",
            getattr(lldb, "eStopReasonThreadExiting", object()): "thread-exiting",
            getattr(lldb, "eStopReasonNone", object()): None,
            getattr(lldb, "eStopReasonInvalid", object()): None,
        }
        return mapping.get(reason, str(reason))

    def _thread_stop_description(self, thread) -> str | None:
        stream = self._lldb.SBStream()
        thread.GetStatus(stream)
        text = stream.GetData().strip()
        return text or None

    def _thread_frame_summary(self, thread) -> Dict[str, Any] | None:
        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            if thread.GetNumFrames() <= 0:
                return None
            frame = thread.GetFrameAtIndex(0)
        line_entry = frame.GetLineEntry()
        module = frame.GetModule()
        module_path = (
            self._filespec_path(module.GetFileSpec())
            if module and module.IsValid()
            else None
        )
        return {
            "function": frame.GetFunctionName(),
            "module": os.path.basename(module_path) if module_path else None,
            "module_path": module_path,
            "file": str(line_entry.GetFileSpec()) if line_entry.IsValid() else None,
            "line": line_entry.GetLine() if line_entry.IsValid() else None,
            "address": hex(frame.GetPC()),
        }

    def _hit_breakpoint_ids(self, thread) -> List[int]:
        ids = []
        data_count = thread.GetStopReasonDataCount()
        for index in range(0, data_count, 2):
            bp_id = thread.GetStopReasonDataAtIndex(index)
            if bp_id:
                ids.append(int(bp_id))
        return ids

    def _filespec_path(self, file_spec) -> str | None:
        if not file_spec or not file_spec.IsValid():
            return None
        directory = file_spec.GetDirectory()
        filename = file_spec.GetFilename()
        if directory and filename:
            return os.path.normpath(os.path.join(directory, filename))
        if filename:
            return os.path.normpath(filename)
        text = str(file_spec)
        return os.path.normpath(text) if text else None

    def _set_value(self, variable, value: str):
        error = self._lldb.SBError()
        ok = variable.SetValueFromCString(value, error)
        if not ok or not error.Success():
            raise RuntimeError(f"Set variable failed: {error}")
