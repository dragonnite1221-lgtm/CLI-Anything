# ruff: noqa: F403, F405, E501
from .openscreen_cli_base import *  # noqa: F403
# fmt: off
from .openscreen_cli_p1 import _repl_mode, _repl_speed, _repl_zoom, _session, output  # noqa: E402,E501
from .openscreen_cli_p2 import _repl_trim, cli  # noqa: E402,E501
# fmt: on


@cli.command()
def repl():
    """Start interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from .utils.repl_skin import ReplSkin
    skin = ReplSkin("openscreen", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    COMMANDS = {
        "help":           "Show this help",
        "quit":           "Exit REPL",
        "status":         "Show session status",
        "undo":           "Undo last operation",
        "redo":           "Redo last operation",
        "new [video]":    "Create new project (optional video path)",
        "open <path>":    "Open .openscreen project file",
        "save [path]":    "Save project",
        "info":           "Show project info",
        "set-video <p>":  "Set source video",
        "set <k> <v>":    "Set editor setting",
        "zoom list":      "List zoom regions",
        "zoom add":       "Add zoom (prompts for params)",
        "zoom rm <id>":   "Remove zoom region",
        "speed list":     "List speed regions",
        "speed add":      "Add speed region (prompts)",
        "speed rm <id>":  "Remove speed region",
        "trim list":      "List trim regions",
        "trim add":       "Add trim region (prompts)",
        "trim rm <id>":   "Remove trim region",
        "crop":           "Show crop region",
        "crop set":       "Set crop (prompts)",
        "probe <path>":   "Probe a video file",
        "export <path>":  "Render and export video",
        "preview [recipe]": "Capture a preview bundle",
        "preview-latest [recipe]": "Show the latest preview bundle",
    }

    while True:
        try:
            proj_name = ""
            modified = False
            if _session.is_open:
                proj_name = os.path.basename(_session.project_path or "untitled")
                modified = _session.is_modified

            line = skin.get_input(pt_session, project_name=proj_name, modified=modified)
            if not line:
                continue

            parts = line.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                if _session.is_modified:
                    skin.warning("Unsaved changes! Use 'save' first or 'quit' again.")
                    _session._modified = False  # Allow next quit
                    continue
                break

            elif cmd == "help":
                skin.help(COMMANDS)

            elif cmd == "status":
                result = _session.status()
                output(result)

            elif cmd == "undo":
                if _session.undo():
                    skin.success("Undone")
                else:
                    skin.warning("Nothing to undo")

            elif cmd == "redo":
                if _session.redo():
                    skin.success("Redone")
                else:
                    skin.warning("Nothing to redo")

            elif cmd == "new":
                video = parts[1] if len(parts) > 1 else None
                proj_mod.new_project(_session, video)
                skin.success("New project created")

            elif cmd == "open":
                if len(parts) < 2:
                    skin.error("Usage: open <path>")
                    continue
                proj_mod.open_project(_session, parts[1])
                skin.success(f"Opened: {parts[1]}")

            elif cmd == "save":
                path = parts[1] if len(parts) > 1 else None
                result = proj_mod.save_project(_session, path)
                skin.success(f"Saved: {result['path']}")

            elif cmd == "info":
                result = proj_mod.info(_session)
                output(result)

            elif cmd == "set-video":
                if len(parts) < 2:
                    skin.error("Usage: set-video <path>")
                    continue
                proj_mod.set_video(_session, parts[1])
                skin.success(f"Video set: {parts[1]}")

            elif cmd == "set":
                if len(parts) < 3:
                    skin.error("Usage: set <key> <value>")
                    continue
                val = parts[2]
                if val.lower() in ("true", "false"):
                    val = val.lower() == "true"
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                proj_mod.set_setting(_session, parts[1], val)
                skin.success(f"{parts[1]} = {val}")

            elif cmd == "zoom":
                _repl_zoom(parts[1:], skin, pt_session)

            elif cmd == "speed":
                _repl_speed(parts[1:], skin, pt_session)

            elif cmd == "trim":
                _repl_trim(parts[1:], skin, pt_session)

            elif cmd == "crop":
                if len(parts) > 1 and parts[1] == "set":
                    skin.info("Enter crop (normalized 0-1):")
                    x = float(skin.sub_input("  x: ", pt_session) or "0")
                    y = float(skin.sub_input("  y: ", pt_session) or "0")
                    w = float(skin.sub_input("  width: ", pt_session) or "1")
                    h = float(skin.sub_input("  height: ", pt_session) or "1")
                    tl_mod.set_crop(_session, x, y, w, h)
                    skin.success("Crop updated")
                else:
                    result = tl_mod.get_crop(_session)
                    output(result)

            elif cmd == "probe":
                if len(parts) < 2:
                    skin.error("Usage: probe <path>")
                    continue
                result = media_mod.probe(parts[1])
                output(result)

            elif cmd == "export":
                if len(parts) < 2:
                    skin.error("Usage: export <output_path>")
                    continue
                def on_prog(stage, msg):
                    skin.info(f"[{stage}] {msg}")
                result = export_mod.render(_session, parts[1], on_prog)
                skin.success(f"Exported: {result['output']} ({result['file_size']} bytes)")

            elif cmd == "preview":
                recipe = parts[1] if len(parts) > 1 else "quick"
                result = preview_mod.capture(_session, recipe=recipe)
                output(result, f"Preview bundle: {result.get('_bundle_dir', '')}")

            elif cmd == "preview-latest":
                recipe = parts[1] if len(parts) > 1 else None
                result = preview_mod.latest(project_path=_session.project_path, recipe=recipe)
                output(result, f"Latest preview bundle: {result.get('_bundle_dir', '')}")

            else:
                skin.warning(f"Unknown command: {cmd}. Type 'help' for commands.")

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            break
        except Exception as e:
            skin.error(str(e))

    skin.print_goodbye()
