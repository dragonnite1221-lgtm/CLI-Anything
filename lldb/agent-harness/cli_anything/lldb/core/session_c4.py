# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin4:
    def modules(self) -> Dict[str, Any]:
        self._require_target()
        modules = []
        for index in range(self.target.GetNumModules()):
            module = self.target.GetModuleAtIndex(index)
            file_spec = module.GetFileSpec()
            path = self._filespec_path(file_spec)
            header_addr = module.GetObjectFileHeaderAddress()
            load_addr = (
                header_addr.GetLoadAddress(self.target)
                if header_addr and header_addr.IsValid()
                else None
            )
            modules.append(
                {
                    "id": index + 1,
                    "name": os.path.basename(path) if path else str(file_spec),
                    "path": path,
                    "symbol_status": "loaded"
                    if module.GetNumCompileUnits() > 0
                    else "unknown",
                    "address": hex(load_addr)
                    if load_addr and load_addr != self._lldb.LLDB_INVALID_ADDRESS
                    else None,
                    "version": module.GetVersion(),
                }
            )
        return {"modules": modules}

    def load_core(self, core_path: str) -> Dict[str, Any]:
        self._require_target()
        self.process = self.target.LoadCore(core_path)
        if not self.process or not self.process.IsValid():
            raise RuntimeError(f"Failed to load core: {core_path}")
        self._process_origin = "core"
        return self.process_info()

    def destroy(self):
        if self.process and self.process.IsValid():
            try:
                if self._process_origin == "attached":
                    self.process.Detach()
                elif self._process_origin == "launched":
                    state = self.process.GetState()
                    if state not in (
                        self._lldb.eStateDetached,
                        self._lldb.eStateExited,
                    ):
                        self.process.Kill()
            except Exception:
                pass
            finally:
                self.process = None
                self._process_origin = None
        self._lldb.SBDebugger.Destroy(self.debugger)
        self._lldb.SBDebugger.Terminate()

    def session_status(self) -> Dict[str, Any]:
        has_target = bool(self.target and self.target.IsValid())
        has_process = bool(self.process and self.process.IsValid())
        return {
            "has_target": has_target,
            "has_process": has_process,
            "process_origin": self._process_origin if has_process else None,
        }

    def process_info(self) -> Dict[str, Any]:
        return self._process_info()

    def _require_target(self):
        if self.target is None or not self.target.IsValid():
            raise RuntimeError("No target. Create target first.")

    def _require_process(self):
        if self.process is None or not self.process.IsValid():
            raise RuntimeError("No process. Launch/attach or load core first.")

    def _current_thread(self):
        self._require_process()
        thread = self.process.GetSelectedThread()
        if not thread or not thread.IsValid():
            if self.process.GetNumThreads() > 0:
                thread = self.process.GetThreadAtIndex(0)
                self.process.SetSelectedThread(thread)
            else:
                raise RuntimeError("No thread available.")
        return thread

    def _current_frame(self):
        thread = self._current_thread()
        frame = thread.GetSelectedFrame()
        if not frame or not frame.IsValid():
            if thread.GetNumFrames() > 0:
                frame = thread.GetFrameAtIndex(0)
                thread.SetSelectedFrame(0)
            else:
                raise RuntimeError("No frame available.")
        return frame

    def _process_info(self) -> Dict[str, Any]:
        self._require_process()
        state = self.process.GetState()
        selected = self.process.GetSelectedThread()
        selected_thread_id = (
            selected.GetThreadID() if selected and selected.IsValid() else None
        )
        return {
            "pid": self.process.GetProcessID(),
            "state": self._STATE_NAMES.get(state, str(state)),
            "num_threads": self.process.GetNumThreads(),
            "selected_thread_id": selected_thread_id,
            "stop": self._stop_info(selected)
            if selected_thread_id is not None
            else None,
            "exit_status": self.process.GetExitStatus(),
        }

    def _frame_info(self) -> Dict[str, Any]:
        f = self._current_frame()
        line_entry = f.GetLineEntry()
        return {
            "function": f.GetFunctionName(),
            "file": str(line_entry.GetFileSpec()) if line_entry.IsValid() else None,
            "line": line_entry.GetLine() if line_entry.IsValid() else None,
            "address": hex(f.GetPC()),
        }
