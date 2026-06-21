# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin1:
    def breakpoint_set(
        self,
        file: Optional[str] = None,
        line: Optional[int] = None,
        function: Optional[str] = None,
        condition: Optional[str] = None,
        allow_pending: bool = False,
    ) -> Dict[str, Any]:
        self._require_target()
        if function:
            bp = self.target.BreakpointCreateByName(function)
        elif file and line:
            bp = self.target.BreakpointCreateByLocation(file, line)
        else:
            raise ValueError("Specify --file/--line or --function")
        if not bp or not bp.IsValid():
            raise RuntimeError("Failed to create breakpoint")
        if condition:
            bp.SetCondition(condition)
        details = self._breakpoint_payload(bp)
        if not details["resolved"] and not allow_pending:
            bp_id = bp.GetID()
            self.target.BreakpointDelete(bp_id)
            raise RuntimeError(
                "Breakpoint is unresolved. Pass allow_pending=True or use "
                "the CLI --allow-pending flag if a pending breakpoint is intended."
            )
        return details

    def breakpoint_list(self) -> Dict[str, Any]:
        self._require_target()
        bps = []
        for i in range(self.target.GetNumBreakpoints()):
            bp = self.target.GetBreakpointAtIndex(i)
            bps.append(self._breakpoint_payload(bp))
        return {"breakpoints": bps}

    def breakpoint_delete(self, bp_id: int) -> Dict[str, Any]:
        self._require_target()
        deleted = self.target.BreakpointDelete(bp_id)
        if not deleted:
            raise RuntimeError(f"Failed to delete breakpoint: {bp_id}")
        return {"deleted": bp_id}

    def breakpoint_enable(self, bp_id: int, enabled: bool = True) -> Dict[str, Any]:
        self._require_target()
        bp = self.target.FindBreakpointByID(bp_id)
        if not bp or not bp.IsValid():
            raise RuntimeError(f"Breakpoint not found: {bp_id}")
        bp.SetEnabled(enabled)
        return {"id": bp_id, "enabled": bool(enabled)}

    def step_over(self) -> Dict[str, Any]:
        self._current_thread().StepOver()
        return self._frame_info()

    def step_into(self) -> Dict[str, Any]:
        self._current_thread().StepInto()
        return self._frame_info()

    def step_out(self) -> Dict[str, Any]:
        self._current_thread().StepOut()
        return self._frame_info()

    def continue_exec(self) -> Dict[str, Any]:
        self._require_process()
        error = self.process.Continue()
        if error is not None and not error.Success():
            raise RuntimeError(f"Continue failed: {error}")
        return self._process_info()

    def interrupt(self) -> Dict[str, Any]:
        self._require_process()
        error = self.process.Stop()
        if error is not None and not error.Success():
            raise RuntimeError(f"Interrupt failed: {error}")
        return self._process_info()

    def interrupt_async(self) -> Dict[str, Any]:
        self._require_process()
        error = self.process.SendAsyncInterrupt()
        if error is not None and not error.Success():
            raise RuntimeError(f"Async interrupt failed: {error}")
        return {"status": "interrupt_requested"}

    def backtrace(self, limit: int = 50) -> Dict[str, Any]:
        thread = self._current_thread()
        frames = []
        for i in range(min(thread.GetNumFrames(), limit)):
            f = thread.GetFrameAtIndex(i)
            line_entry = f.GetLineEntry()
            frames.append(
                {
                    "index": i,
                    "function": f.GetFunctionName(),
                    "file": str(line_entry.GetFileSpec())
                    if line_entry.IsValid()
                    else None,
                    "line": line_entry.GetLine() if line_entry.IsValid() else None,
                    "address": hex(f.GetPC()),
                }
            )
        return {
            "thread_id": thread.GetThreadID(),
            "frames": frames,
            "total_frames": thread.GetNumFrames(),
        }

    def locals(self) -> Dict[str, Any]:
        frame = self._current_frame()
        variables = frame.GetVariables(True, True, False, True)
        result = []
        for v in variables:
            result.append(
                {
                    "name": v.GetName(),
                    "type": v.GetTypeName(),
                    "value": v.GetValue(),
                    "summary": v.GetSummary(),
                    "num_children": v.GetNumChildren(),
                }
            )
        return {"variables": result}
