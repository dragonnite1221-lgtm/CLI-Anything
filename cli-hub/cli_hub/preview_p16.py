# ruff: noqa: F403, F405, E501
from .preview_base import *  # noqa: F403


def _render_live_html_fs0_5():
    return f"""    }}

    function renderCommands(session) {{
      const commands = [
        session.publish_command,
        session.watch_command,
        session.inspect_command,
      ].filter(Boolean);
      const strip = document.getElementById("command-strip");
      strip.innerHTML = commands.map((command) => `<div class="command-chip">${{escapeHtml(command)}}</div>`).join("");
    }}

    function artifactUrl(session, artifact) {{
      const currentLink = safeRelativeUrlPath(CURRENT_LINK);
      const artifactPath = safeRelativeUrlPath(artifact && artifact.path);
      if (!currentLink || !artifactPath) {{
        return null;
      }}
      const rev = encodeURIComponent(session.updated_at || Date.now());
      return `${{currentLink}}/${{artifactPath}}?rev=${{rev}}`;
    }}

    function pickArtifact(manifest, role, mediaPrefix) {{
      return (manifest.artifacts || []).find((artifact) => artifact.role === role)
        || (manifest.artifacts || []).find((artifact) => (artifact.media_type || "").startsWith(mediaPrefix));
    }}

    function renderHero(session, manifest) {{
      const hero = pickArtifact(manifest, "hero", "image/");
      const slot = document.getElementById("hero-slot");
      const meta = document.getElementById("hero-meta");
      if (!hero) {{
        slot.innerHTML = '<div class="empty">No hero frame was published in the current bundle.</div>';
        meta.textContent = "No hero frame";
        return;
      }}
      const url = artifactUrl(session, hero);
      if (!url) {{
        slot.innerHTML = '<div class="empty">Hero frame path is invalid.</div>';
        meta.textContent = "Invalid hero frame path";
        return;
      }}
      slot.innerHTML = `<img class="hero-frame" src="${{escapeHtml(url)}}" alt="${{escapeHtml(hero.label || hero.artifact_id || "Hero frame")}}">`;
      const bits = [];
      if (hero.width && hero.height) bits.push(`${{hero.width}}×${{hero.height}}`);
      if (hero.time_s != null) bits.push(`t=${{hero.time_s}}s`);
      meta.textContent = bits.join(" · ") || (hero.label || "Hero frame");
    }}

    function renderClip(session, manifest) {{
      const clip = pickArtifact(manifest, "preview-clip", "video/");
      const slot = document.getElementById("clip-slot");
      const meta = document.getElementById("clip-meta");
      if (!clip) {{
        slot.innerHTML = '<div class="empty">No preview clip was published in the current bundle.</div>';
        meta.textContent = "No clip";
        return;
      }}
      const url = artifactUrl(session, clip);
      if (!url) {{
        slot.innerHTML = '<div class="empty">Preview clip path is invalid.</div>';
        meta.textContent = "Invalid clip path";
        return;
      }}
      slot.innerHTML = `
        <video class="hero-frame" controls preload="metadata" src="${{escapeHtml(url)}}">
          Your browser does not support embedded video.
        </video>
      `;
      const bits = [];
      if (clip.width && clip.height) bits.push(`${{clip.width}}×${{clip.height}}`);
      if (clip.duration_s != null) bits.push(`${{clip.duration_s}}s`);
      if (clip.render_method) bits.push(clip.render_method);
      meta.textContent = bits.join(" · ") || (clip.label || "Preview clip");
    }}

    function renderGallery(session, manifest) {{
      const items = (manifest.artifacts || [])
        .filter((artifact) => artifact.role === "gallery" && (artifact.media_type || "").startsWith("image/"));
      const root = document.getElementById("gallery");
      if (!items.length) {{
        root.innerHTML = '<div class="empty">No gallery frames were published in the current bundle.</div>';
        return;
      }}
      const cards = items.map((artifact) => {{
        const url = artifactUrl(session, artifact);
        if (!url) return "";
        return `
          <article class="thumb">
            <img src="${{escapeHtml(url)}}" alt="${{escapeHtml(artifact.label || artifact.artifact_id || "Gallery frame")}}">
            <div class="label">${{escapeHtml(artifact.label || artifact.artifact_id || "Frame")}}</div>
            <div class="meta">${{artifact.time_s != null ? `t=${{artifact.time_s}}s` : ""}}</div>
          </article>
        `;
      }}).filter(Boolean);
      root.innerHTML = cards.length
        ? cards.join("")
        : '<div class="empty">No valid gallery frame paths were published in the current bundle.</div>';
    }}

    function renderNotes(session, manifest, summary, trajectory) {{
      const warnings = summary.warnings || manifest.warnings || [];
      const actions = summary.next_actions || [];
      const notes = document.getElementById("notes");
      const lines = [
        `<div><strong>Current bundle</strong><br>${{escapeHtml(session.current_bundle_id || manifest.bundle_id || "n/a")}}</div>`,
        `<div><strong>Current step</strong><br>${{escapeHtml(trajectory.currentStepId || session.current_step_id || "n/a")}}</div>`,
        `<div><strong>Session path</strong><br>${{escapeHtml(session.project_path || session.project_name || "n/a")}}</div>`,
        `<div><strong>Last update</strong><br>${{escapeHtml(session.updated_at || "unknown")}}</div>`,
      ];
      if (trajectory.recentCommand) {{
        lines.push(`<div><strong>Latest command</strong><br>${{escapeHtml(trajectory.recentCommand)}}</div>`);
      }}
      if (trajectory.recentPublishReason) {{
        lines.push(`<div><strong>Latest publish reason</strong><br>${{escapeHtml(trajectory.recentPublishReason)}}</div>`);
      }}
      if (warnings.length) {{
        lines.push(`<div><strong>Warnings</strong><ul>${{warnings.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul></div>`);
      }}
      if (actions.length) {{
"""
