# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin0:
    """Encapsulates one LLDB debugger session using Python API only."""

    _STATE_NAMES = {
        0: "invalid",
        1: "unloaded",
        2: "connected",
        3: "attaching",
        4: "launching",
        5: "stopped",
        6: "running",
        7: "stepping",
        8: "crashed",
        9: "detached",
        10: "exited",
        11: "suspended",
    }

    def __init__(self):
        self._lldb = ensure_lldb_importable()
        self._lldb.SBDebugger.Initialize()
        self.debugger = self._lldb.SBDebugger.Create()
        self.debugger.SetAsync(False)
        self.target = None
        self.process = None
        self._process_origin: str | None = None

    def target_create(
        self, exe_path: str, arch: Optional[str] = None
    ) -> Dict[str, Any]:
        arch = arch or self._lldb.LLDB_ARCH_DEFAULT
        self.target = self.debugger.CreateTargetWithFileAndArch(exe_path, arch)
        if not self.target or not self.target.IsValid():
            raise RuntimeError(f"Failed to create target: {exe_path}")
        return {
            "executable": exe_path,
            "arch": arch,
            "triple": self.target.GetTriple(),
        }

    def target_create_empty(self, arch: Optional[str] = None) -> Dict[str, Any]:
        """Create an empty target for attach flows without a known executable."""
        if arch:
            self.target = self.debugger.CreateTargetWithFileAndArch("", arch)
        else:
            self.target = self.debugger.CreateTarget("")
        if not self.target or not self.target.IsValid():
            raise RuntimeError("Failed to create empty attach target")
        return {
            "executable": None,
            "arch": arch,
            "triple": self.target.GetTriple(),
        }

    def target_info(self) -> Dict[str, Any]:
        self._require_target()
        exe = self.target.GetExecutable()
        return {
            "triple": self.target.GetTriple(),
            "executable": str(exe) if exe else None,
            "byte_order": str(self.target.GetByteOrder()),
            "address_byte_size": self.target.GetAddressByteSize(),
            "num_modules": self.target.GetNumModules(),
            "num_breakpoints": self.target.GetNumBreakpoints(),
        }

    def attach_pid(self, pid: int) -> Dict[str, Any]:
        self._require_target()
        attach_info = self._lldb.SBAttachInfo()
        attach_info.SetProcessID(pid)
        return self._attach(attach_info)

    def attach_name(self, name: str, wait_for: bool = False) -> Dict[str, Any]:
        self._require_target()
        attach_info = self._lldb.SBAttachInfo()
        attach_info.SetExecutable(name)
        if wait_for:
            attach_info.SetWaitForLaunch(True, False)
        return self._attach(attach_info)

    def _attach(self, attach_info) -> Dict[str, Any]:
        error = self._lldb.SBError()
        self.process = self.target.Attach(attach_info, error)
        if not error.Success():
            raise RuntimeError(f"Attach failed: {error}")
        self._process_origin = "attached"
        return self.process_info()

    def launch(
        self,
        args: Optional[List[str]] = None,
        env: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        stop_at_entry: bool = False,
        suppress_stdio: bool = False,
    ) -> Dict[str, Any]:
        self._require_target()
        error = self._lldb.SBError()
        launch_info = self._lldb.SBLaunchInfo(args or [])
        launch_info.SetWorkingDirectory(working_dir or os.getcwd())
        if env:
            launch_info.SetEnvironmentEntries(env, True)
        if stop_at_entry:
            launch_info.SetLaunchFlags(self._lldb.eLaunchFlagStopAtEntry)
        if suppress_stdio:
            launch_info.AddSuppressFileAction(1, False, True)
            launch_info.AddSuppressFileAction(2, False, True)
        self.process = self.target.Launch(launch_info, error)
        if not error.Success():
            raise RuntimeError(f"Launch failed: {error}")
        if not self.process or not self.process.IsValid():
            raise RuntimeError("Launch failed")
        self._process_origin = "launched"
        return self.process_info()

    def detach(self) -> Dict[str, Any]:
        self._require_process()
        error = self.process.Detach()
        if not error.Success():
            raise RuntimeError(f"Detach failed: {error}")
        self.process = None
        self._process_origin = None
        return {"status": "detached"}
