# ruff: noqa: F403, F405, E501
from .session_base import *  # noqa: F403


class LLDBSessionMixin3:
    def find_memory(
        self,
        needle: str,
        start_address: int,
        size: int,
        *,
        chunk_size: int = MEMORY_FIND_CHUNK_SIZE,
        max_scan_size: int = MEMORY_FIND_MAX_SCAN_SIZE,
    ) -> Dict[str, Any]:
        self._require_process()
        if not needle:
            raise ValueError("Needle must not be empty")
        if size <= 0:
            raise ValueError("Scan size must be positive")
        if size > max_scan_size:
            raise ValueError(
                f"Scan size exceeds max supported scan size ({max_scan_size} bytes)"
            )
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")

        needle_bytes = needle.encode("utf-8")
        overlap = max(0, len(needle_bytes) - 1)
        remaining = size
        current = start_address
        trailing = b""

        while remaining > 0:
            read_size = min(chunk_size, remaining)
            chunk = bytes.fromhex(self.read_memory(current, read_size)["hex"])
            haystack = trailing + chunk
            idx = haystack.find(needle_bytes)
            if idx >= 0:
                base = current - len(trailing)
                return {
                    "needle": needle,
                    "start": hex(start_address),
                    "size": size,
                    "found": True,
                    "address": hex(base + idx),
                    "chunk_size": chunk_size,
                    "max_scan_size": max_scan_size,
                }

            trailing = haystack[-overlap:] if overlap else b""
            current += read_size
            remaining -= read_size

        return {
            "needle": needle,
            "start": hex(start_address),
            "size": size,
            "found": False,
            "address": None,
            "chunk_size": chunk_size,
            "max_scan_size": max_scan_size,
        }

    def disassemble(self, address: int, count: int = 8) -> Dict[str, Any]:
        self._require_target()
        sb_address = self.target.ResolveLoadAddress(address)
        if not sb_address or not sb_address.IsValid():
            raise RuntimeError(f"Could not resolve address: {hex(address)}")
        instructions = self.target.ReadInstructions(sb_address, max(1, count))
        result = []
        for i in range(instructions.GetSize()):
            inst = instructions.GetInstructionAtIndex(i)
            stream = self._lldb.SBStream()
            inst.GetDescription(stream)
            inst_address = inst.GetAddress().GetLoadAddress(self.target)
            result.append(
                {
                    "address": hex(inst_address),
                    "instruction": stream.GetData().strip(),
                }
            )
        return {"instructions": result}

    def loaded_sources(self) -> Dict[str, Any]:
        self._require_target()
        seen = set()
        sources = []
        for module_index in range(self.target.GetNumModules()):
            module = self.target.GetModuleAtIndex(module_index)
            for unit_index in range(module.GetNumCompileUnits()):
                unit = module.GetCompileUnitAtIndex(unit_index)
                file_spec = unit.GetFileSpec()
                path = self._filespec_path(file_spec)
                if not path or path in seen:
                    continue
                seen.add(path)
                sources.append({"name": os.path.basename(path), "path": path})
        return {"sources": sources}
