# ruff: noqa: F403, F405, E501
from .dap_base import *  # noqa: F403


class LLDBDebugAdapterMixin3:
    def _handle_source(self, args: dict[str, Any]):
        source = args.get("source") or {}
        path = source.get("path")
        if not path:
            raise RuntimeError("source request requires source.path")
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        return {"content": text, "mimeType": "text/plain"}, None

    def _handle_loadedSources(self, _args: dict[str, Any]):
        sources = self._ensure_session().loaded_sources().get("sources", [])
        return {
            "sources": [
                self._source_from_path(item.get("path"))
                for item in sources
                if item.get("path")
            ]
        }, None

    def _handle_modules(self, _args: dict[str, Any]):
        modules = []
        for item in self._ensure_session().modules().get("modules", []):
            modules.append(
                {
                    "id": item["id"],
                    "name": item.get("name") or "<unknown>",
                    "path": item.get("path"),
                    "isOptimized": False,
                    "isUserCode": True,
                    "symbolStatus": item.get("symbol_status"),
                    "addressRange": item.get("address"),
                    "version": item.get("version"),
                }
            )
        return {"modules": modules}, None

    def _handle_exceptionInfo(self, _args: dict[str, Any]):
        info = self._ensure_session().process_info()
        stop = info.get("stop") or {}
        reason = stop.get("reason") or "unknown"
        description = stop.get("description") or reason
        return {
            "exceptionId": reason,
            "breakMode": "always",
            "description": description,
            "details": {"message": description},
        }, None

    def _handle_readMemory(self, args: dict[str, Any]):
        address = self._parse_address(str(args.get("memoryReference") or "0"))
        address += int(args.get("offset", 0) or 0)
        count = int(args.get("count", 0) or 0)
        if count <= 0:
            raise RuntimeError("readMemory requires a positive count")
        payload = self._ensure_session().read_memory(address, count)
        data = bytes.fromhex(payload["hex"])
        return {
            "address": hex(address),
            "data": base64.b64encode(data).decode("ascii"),
        }, None

    def _handle_disassemble(self, args: dict[str, Any]):
        address = self._parse_address(str(args.get("memoryReference") or "0"))
        address += int(args.get("instructionOffset", 0) or 0)
        count = int(args.get("instructionCount", 8) or 8)
        payload = self._ensure_session().disassemble(address, count=count)
        instructions = [
            {"address": item["address"], "instruction": item["instruction"]}
            for item in payload.get("instructions", [])
        ]
        return {"instructions": instructions}, None

    def _step_post_send(self, step_fn: Callable[[], dict[str, Any]]):
        def post_send():
            self._reset_refs_for_resume()
            self._send_continued_event()
            with self._lldb_api_lock:
                step_fn()
                self._emit_execution_event(default_reason="step")

        return post_send

    def _start_continue_thread(self, *, name: str, default_reason: str):
        with self._continue_state:
            if self._continue_active:
                self._log(
                    "continue requested while a continue operation is already active"
                )
                return
            self._continue_active = True
        threading.Thread(
            target=self._continue_until_stop,
            kwargs={"default_reason": default_reason},
            name=name,
            daemon=True,
        ).start()

    def _continue_until_stop(self, *, default_reason: str):
        try:
            self._ensure_session().continue_exec()
        except Exception as exc:
            self._log(f"continue failed: {exc}")
            self._send_event(
                "output", {"category": "stderr", "output": f"continue failed: {exc}\n"}
            )
            self._send_event("terminated")
            return
        finally:
            self._mark_continue_inactive()

        with self._lldb_api_lock:
            self._emit_breakpoint_updates()
            self._emit_execution_event(default_reason=default_reason)

    def _mark_continue_inactive(self):
        with self._continue_state:
            self._continue_active = False
            self._continue_state.notify_all()

    def _is_continue_active(self) -> bool:
        with self._continue_state:
            return self._continue_active
