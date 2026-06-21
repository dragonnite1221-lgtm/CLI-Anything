# ruff: noqa: F403, F405, E501
from .native_api_base import *  # noqa: F403


class NativeAPIBackendMixin1:
    def _start_process(
        self, step: MacroStep, params: dict, context: BackendContext, t0: float
    ) -> StepResult:
        """Launch a GUI application in the background without waiting for it to exit.

        Use this instead of run_command for GUI apps like gedit, inkscape, etc.
        The process is detached immediately after launch.

        Params:
          command:    list[str] — the command to run
          cwd:        str       — working directory (optional)
          env:        dict      — extra environment variables (optional)
          log_file:   str       — redirect stdout+stderr here (default /dev/null)
        """
        import subprocess
        step_params = substitute(step.params, params)
        command: list[str] = step_params.get("command", [])
        if not command:
            return StepResult(
                success=False,
                error="NativeAPIBackend.start_process: 'command' param is required.",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        if isinstance(command, str):
            import shlex
            command = shlex.split(command)
        command = [str(c) for c in command]

        cwd: str = step_params.get("cwd", "")
        extra_env: dict = step_params.get("env", {})
        log_file: str = step_params.get("log_file", "/dev/null")

        env = os.environ.copy()
        if extra_env:
            env.update({k: str(v) for k, v in extra_env.items()})

        if context.dry_run:
            return StepResult(
                success=True,
                output={"dry_run": True, "command": command},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )

        try:
            with open(log_file, "a") as log:
                proc = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=log,
                    cwd=cwd or None,
                    env=env,
                    start_new_session=True,   # detach from current process group
                )
            return StepResult(
                success=True,
                output={"pid": proc.pid, "command": command},
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
        except FileNotFoundError as exc:
            return StepResult(
                success=False,
                error=f"Command not found: {command[0]}. {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
        except Exception as exc:
            return StepResult(
                success=False,
                error=f"start_process failed: {exc}",
                backend_used=self.name,
                duration_ms=(time.time() - t0) * 1000,
            )
