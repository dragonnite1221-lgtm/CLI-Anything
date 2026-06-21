# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin2:
    def local_values(self):
        """Return raw SBValue locals for in-process adapters such as DAP."""
        frame = self._current_frame()
        variables = frame.GetVariables(True, True, False, True)
        return [variables.GetValueAtIndex(i) for i in range(variables.GetSize())]

    def set_local_variable(
        self, thread_id: int, frame_index: int, name: str, value: str
    ):
        self.thread_select(thread_id)
        self.frame_select(frame_index)
        frame = self._current_frame()
        variable = frame.FindVariable(name)
        if not variable or not variable.IsValid():
            raise RuntimeError(f"Variable not found: {name}")
        self._set_value(variable, value)
        return variable

    def set_child_value(self, parent, name: str, value: str):
        child = parent.GetChildMemberWithName(name)
        if not child or not child.IsValid():
            for index in range(parent.GetNumChildren()):
                candidate = parent.GetChildAtIndex(index)
                if candidate.GetName() == name:
                    child = candidate
                    break
        if not child or not child.IsValid():
            raise RuntimeError(f"Child variable not found: {name}")
        self._set_value(child, value)
        return child

    def evaluate(self, expr: str) -> Dict[str, Any]:
        frame = self._current_frame()
        val = frame.EvaluateExpression(expr)
        return {
            "expression": expr,
            "type": val.GetTypeName(),
            "value": val.GetValue(),
            "summary": val.GetSummary(),
            "error": str(val.GetError()) if not val.GetError().Success() else None,
        }

    def threads(self) -> Dict[str, Any]:
        self._require_process()
        result = []
        for i in range(self.process.GetNumThreads()):
            t = self.process.GetThreadAtIndex(i)
            desc = self._lldb.SBStream()
            t.GetStatus(desc)
            result.append(
                {
                    "index": i,
                    "id": t.GetThreadID(),
                    "name": t.GetName(),
                    "stop_reason": desc.GetData().strip(),
                    "num_frames": t.GetNumFrames(),
                    "selected": t.GetThreadID()
                    == self.process.GetSelectedThread().GetThreadID(),
                }
            )
        return {"threads": result}

    def thread_select(self, thread_id: int) -> Dict[str, Any]:
        self._require_process()
        thread = self.process.GetThreadByID(thread_id)
        if not thread or not thread.IsValid():
            raise RuntimeError(f"Thread not found: {thread_id}")
        self.process.SetSelectedThread(thread)
        return {"selected_thread_id": thread_id}

    def frame_select(self, index: int) -> Dict[str, Any]:
        thread = self._current_thread()
        if index < 0 or index >= thread.GetNumFrames():
            raise RuntimeError(f"Frame index out of range: {index}")
        frame = thread.GetFrameAtIndex(index)
        thread.SetSelectedFrame(index)
        line_entry = frame.GetLineEntry()
        return {
            "selected_frame_index": index,
            "function": frame.GetFunctionName(),
            "file": str(line_entry.GetFileSpec()) if line_entry.IsValid() else None,
            "line": line_entry.GetLine() if line_entry.IsValid() else None,
        }

    def frame_info(self) -> Dict[str, Any]:
        return self._frame_info()

    def read_memory(self, address: int, size: int) -> Dict[str, Any]:
        self._require_process()
        error = self._lldb.SBError()
        data = self.process.ReadMemory(address, size, error)
        if not error.Success():
            raise RuntimeError(f"Read memory failed: {error}")
        return {
            "address": hex(address),
            "size": size,
            "hex": data.hex(),
        }
