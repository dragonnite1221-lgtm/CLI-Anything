# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_live_html_fs0_3():
    return f"""        if (value === null || value === undefined) continue;
        if (typeof value === "string" && value.trim() === "") continue;
        return value;
      }}
      return null;
    }}

    function safeRelativeUrlPath(value) {{
      const text = String(value ?? "").trim();
      if (!text || text.startsWith("/") || text.includes("\\\\") || text.includes("\\u0000")) {{
        return null;
      }}
      const parts = text.split("/");
      const encoded = [];
      for (const part of parts) {{
        if (!part || part === "." || part === "..") {{
          return null;
        }}
        encoded.push(encodeURIComponent(part));
      }}
      return encoded.join("/");
    }}

    function commandText(value) {{
      if (value === null || value === undefined) return null;
      if (typeof value === "string") return value.trim() || null;
      if (Array.isArray(value)) return value.map((part) => String(part)).join(" ").trim() || null;
      if (typeof value === "object") {{
        return commandText(value.display_cmd || value.command || value.argv || value.raw) || JSON.stringify(value);
      }}
      return String(value);
    }}

    async function fetchJson(path) {{
      const sep = path.includes("?") ? "&" : "?";
      const response = await fetch(`${{path}}${{sep}}ts=${{Date.now()}}`, {{ cache: "no-store" }});
      if (!response.ok) {{
        throw new Error(`Failed to load ${{path}} (${{response.status}})`);
      }}
      return response.json();
    }}

    function setStatus(text, isError = false) {{
      const chip = document.getElementById("status-chip");
      chip.textContent = text;
      chip.dataset.state = isError ? "error" : "ok";
    }}

    function collectTrajectoryHints(node, state) {{
      if (!node || typeof node !== "object") return;
      if (state.seen.has(node)) return;
      state.seen.add(node);
      if (Array.isArray(node)) {{
        for (const item of node) collectTrajectoryHints(item, state);
        return;
      }}
      for (const [key, value] of Object.entries(node)) {{
        const lower = String(key).toLowerCase();
        if ((lower === "trajectory" || lower === "timeline") && value && typeof value === "object" && !Array.isArray(value)) {{
          state.embedded ||= value;
        }}
        if ((lower === "trajectory" || lower === "timeline" || lower.endsWith("_trajectory") || lower.endsWith("_timeline")) && typeof value === "string") {{
          state.refs.add(value);
        }}
        if ((lower === "trajectory_path" || lower === "timeline_path" || lower === "trajectory_ref" || lower === "timeline_ref") && typeof value === "string") {{
          state.refs.add(value);
        }}
        if (value && typeof value === "object") {{
          collectTrajectoryHints(value, state);
        }}
      }}
    }}

    function collectTrajectoryCandidates(session) {{
      const state = {{ refs: new Set(TRAJECTORY_CANDIDATES), embedded: null, seen: new Set() }};
      collectTrajectoryHints(session, state);
      return {{ refs: Array.from(state.refs), embedded: state.embedded }};
    }}

    async function fetchTrajectory(session) {{
      const hints = collectTrajectoryCandidates(session);
      if (hints.embedded) {{
        return {{ raw: hints.embedded, ref: "embedded:session" }};
      }}
      for (const ref of hints.refs) {{
        try {{
          const raw = await fetchJson(ref);
          return {{ raw, ref }};
        }} catch (_error) {{
        }}
      }}
      return null;
    }}

    function normalizeTimelineItem(item, fallbackIndex) {{
      const bundle = (item && typeof item === "object" && !Array.isArray(item))
        ? (item.copied_bundle || item.bundle || item.preview_bundle || item.current_bundle || item.published_bundle || item)
        : {{}};
      const stepIndex = Number.parseInt(firstDefined(item?.step_index, item?.index, item?.sequence_index, fallbackIndex), 10);
      const returnCode = item?.returncode;
      return {{
        orderIndex: fallbackIndex,
        stepIndex: Number.isFinite(stepIndex) ? stepIndex : fallbackIndex,
        stepId: String(firstDefined(item?.step_id, item?.id, item?.command_id, `step-${{fallbackIndex}}`)),
        stepLabel: firstDefined(item?.step_label, item?.label, item?.title, item?.name, item?.stage_title, item?.stage_label),
        command: commandText(firstDefined(item?.command, item?.display_cmd, item?.display_command, item?.argv, item?.raw_command)),
        commandStartedAt: firstDefined(item?.command_started_at, item?.started_at, item?.timeline_start_s, item?.start_s),
        commandFinishedAt: firstDefined(item?.command_finished_at, item?.finished_at, item?.timeline_end_s, item?.end_s, item?.completed_at),
        createdAt: firstDefined(item?.created_at, item?.timeline_ready_s, item?.ready_at, item?.published_at),
        publishReason: firstDefined(item?.publish_reason, item?.reason),
        bundleId: firstDefined(item?.bundle_id, bundle?.bundle_id),
        bundleDir: firstDefined(item?.bundle_dir, bundle?.bundle_dir),
        manifestPath: firstDefined(item?.manifest_path, bundle?.manifest_path),
        summaryPath: firstDefined(item?.summary_path, bundle?.summary_path),
        status: firstDefined(item?.status, returnCode === 0 ? "ok" : null),
        cached: item?.cached,
        sourceFingerprint: item?.source_fingerprint,
        note: firstDefined(item?.note, item?.stage_story, item?.story, item?.description),
      }};
    }}
"""
