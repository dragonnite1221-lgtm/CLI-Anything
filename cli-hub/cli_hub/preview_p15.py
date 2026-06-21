# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_live_html_fs0_4():
    return f"""
    function normalizeLegacyHistory(session) {{
      const history = Array.isArray(session.history) ? session.history : [];
      const entries = history.map((item, index) => normalizeTimelineItem(item, index));
      return {{
        mode: "legacy-history",
        sourceLabel: "session.history",
        stepCount: firstDefined(session.trajectory_step_count, entries.length, 0),
        currentStepId: session.current_step_id || null,
        recentCommand: session.latest_command || null,
        recentPublishReason: firstDefined(session.latest_publish_reason, session.source_state?.last_publish_reason),
        publishedBundleCount: entries.filter((entry) => entry.bundleId).length,
        entries,
      }};
    }}

    function normalizeTrajectory(session, payload) {{
      if (!payload || !payload.raw || typeof payload.raw !== "object") {{
        return normalizeLegacyHistory(session);
      }}

      const raw = payload.raw;
      const commands = Array.isArray(raw.commands) ? raw.commands : [];
      const entries = [];
      const byId = new Map();
      const byIndex = new Map();

      for (let index = 0; index < commands.length; index += 1) {{
        const row = normalizeTimelineItem(commands[index], index);
        entries.push(row);
        byId.set(row.stepId, row);
        byIndex.set(row.stepIndex, row);
      }}

      let events = [];
      for (const key of ["steps", "preview_events", "entries", "events", "history", "timeline", "publishes"]) {{
        if (Array.isArray(raw[key]) && raw[key].length) {{
          events = raw[key];
          break;
        }}
      }}

      for (let index = 0; index < events.length; index += 1) {{
        const row = normalizeTimelineItem(events[index], index);
        const existing = byId.get(row.stepId) || byIndex.get(row.stepIndex);
        if (!existing) {{
          entries.push(row);
          byId.set(row.stepId, row);
          byIndex.set(row.stepIndex, row);
          continue;
        }}
        for (const key of [
          "stepLabel",
          "command",
          "commandStartedAt",
          "commandFinishedAt",
          "createdAt",
          "publishReason",
          "bundleId",
          "bundleDir",
          "manifestPath",
          "summaryPath",
          "status",
          "cached",
          "sourceFingerprint",
          "note",
        ]) {{
          existing[key] = firstDefined(existing[key], row[key]);
        }}
      }}

      if (!entries.length) {{
        return normalizeLegacyHistory(session);
      }}

      entries.sort((left, right) =>
        (left.stepIndex - right.stepIndex)
        || (left.orderIndex - right.orderIndex)
        || String(left.commandFinishedAt || left.createdAt || "").localeCompare(String(right.commandFinishedAt || right.createdAt || ""))
      );

      const recentCommandEntry = [...entries].reverse().find((entry) => entry.command);
      const recentPublishEntry = [...entries].reverse().find((entry) => entry.publishReason || entry.bundleId);

      return {{
        mode: "trajectory",
        protocol: raw.protocol_version || raw.protocol || session.trajectory_protocol_version || null,
        sourceLabel: payload.ref || session.trajectory_path || "trajectory.json",
        stepCount: firstDefined(raw.step_count, session.trajectory_step_count, commands.length || entries.length, 0),
        currentStepId: firstDefined(raw.current_step_id, session.current_step_id, recentPublishEntry?.stepId, recentCommandEntry?.stepId),
        recentCommand: firstDefined(session.latest_command, raw.latest_command, recentCommandEntry?.command),
        recentPublishReason: firstDefined(session.latest_publish_reason, raw.latest_publish_reason, recentPublishEntry?.publishReason),
        publishedBundleCount: entries.filter((entry) => entry.bundleId).length,
        entries,
      }};
    }}

    function renderFacts(session, manifest, summary, trajectory) {{
      const facts = Object.assign(
        {{
          software: manifest.software || session.software || "unknown",
          recipe: manifest.recipe || session.recipe || "unknown",
          bundle: manifest.bundle_id || session.current_bundle_id || "n/a",
          step_count: trajectory.stepCount || session.trajectory_step_count || "n/a",
          current_step: trajectory.currentStepId || session.current_step_id || "n/a",
          publish_reason: trajectory.recentPublishReason || session.latest_publish_reason || "n/a",
          updated: session.updated_at || "unknown",
        }},
        summary.facts || {{}}
      );
      const row = document.getElementById("fact-row");
      row.innerHTML = Object.entries(facts)
        .slice(0, 9)
        .map(([key, value]) => `
          <div class="fact-card">
            <span>${{escapeHtml(key)}}</span>
            <strong>${{escapeHtml(value)}}</strong>
          </div>
        `)
        .join("");
"""
