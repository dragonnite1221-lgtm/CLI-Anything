# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin0:
    """Single-session stdio DAP adapter for LLDB."""

    def __init__(
        self,
        session_factory: Callable[[], LLDBSession] = LLDBSession,
        log_file: str | None = None,
        profile_file: str | None = None,
    ):
        self._session_factory = session_factory
        self._session: LLDBSession | None = None
        self._out: BinaryIO | None = None
        self._seq = 1
        self._pending_launch: dict[str, Any] | None = None
        self._pending_attach: dict[str, Any] | None = None
        self._source_breakpoints: dict[str, list[int]] = {}
        self._function_breakpoints: list[int] = []
        self._frame_refs: dict[int, tuple[int, int]] = {}
        self._variable_refs: dict[int, dict[str, Any]] = {}
        self._next_ref = 1
        self._log_file = Path(log_file).expanduser() if log_file else None
        self._protocol_lock = threading.Lock()
        self._lldb_api_lock = threading.RLock()
        self._continue_state = threading.Condition()
        self._continue_active = False
        self._auto_continue_internal_breakpoints = False
        self._base_auto_continue_internal_breakpoints = False
        self._base_stop_rules: list[StopRule] = []
        self._active_stop_rules: list[StopRule] = []
        self._pause_requested = False
        self._mutation_stop_timeout = 10.0
        if profile_file:
            self._base_stop_rules, self._base_auto_continue_internal_breakpoints = (
                self._load_stop_profile_file(profile_file)
            )
            self._active_stop_rules = list(self._base_stop_rules)

    def run(
        self, instream: BinaryIO | None = None, outstream: BinaryIO | None = None
    ) -> int:
        instream = instream or sys.stdin.buffer
        outstream = outstream or sys.stdout.buffer
        self._out = outstream
        try:
            while True:
                try:
                    message = read_message(instream)
                except DAPProtocolError as exc:
                    self._log(f"DAP protocol error: {exc}")
                    return 1
                if message is None:
                    return 0
                self.handle_message(message)
        finally:
            self._cleanup_session()

    def handle_message(self, message: dict[str, Any]):
        if message.get("type") != "request":
            return

        request_seq = int(message.get("seq", 0))
        command = str(message.get("command") or "")
        args = message.get("arguments") or {}
        handler = getattr(self, f"_handle_{command}", None)
        if handler is None:
            self._send_response(
                request_seq,
                command,
                success=False,
                message=f"Unsupported request: {command}",
            )
            return

        try:
            body, post_send = handler(args)
        except Exception as exc:
            self._log(f"{command} failed: {exc}")
            self._send_response(request_seq, command, success=False, message=str(exc))
            return

        self._send_response(request_seq, command, body=body)
        if post_send:
            try:
                post_send()
            except Exception as exc:
                self._log(f"{command} post-response failed: {exc}")
                self._send_event(
                    "output",
                    {
                        "category": "stderr",
                        "output": f"{command} failed after response: {exc}\n",
                    },
                )
                self._send_event("terminated")

    def _handle_initialize(self, _args: dict[str, Any]):
        capabilities = {
            "supportsConfigurationDoneRequest": True,
            "supportsFunctionBreakpoints": True,
            "supportsEvaluateForHovers": True,
            "supportsDisassembleRequest": True,
            "supportsLoadedSourcesRequest": True,
            "supportsReadMemoryRequest": True,
            "supportsSetVariable": True,
            "supportsModulesRequest": True,
            "supportsExceptionInfoRequest": True,
            "supportsSteppingGranularity": False,
            "supportTerminateDebuggee": True,
        }
        return capabilities, lambda: self._send_event("initialized")

    def _handle_launch(self, args: dict[str, Any]):
        program = args.get("program") or args.get("executable")
        if not program:
            raise RuntimeError("launch requires 'program'")
        self._ensure_session().target_create(str(program), arch=args.get("arch"))
        self._pending_launch = {
            "args": self._coerce_args(args.get("args")),
            "env": self._coerce_env(args.get("env")),
            "working_dir": args.get("cwd") or args.get("workingDirectory"),
            "stop_at_entry": bool(args.get("stopOnEntry", False)),
            "suppress_stdio": True,
        }
        self._configure_stop_rules(args)
        self._pending_attach = None
        return {}, None
