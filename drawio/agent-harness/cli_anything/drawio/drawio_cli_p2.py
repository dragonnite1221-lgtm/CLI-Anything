# ruff: noqa: F403, F405, E501
from .drawio_cli_base import *  # noqa: F403

# fmt: off
from .drawio_cli_p1 import REPL_COMMANDS, _print_dict  # noqa: E402,E501
# fmt: on


def _run_repl(s: Session, skin):
    """Run the interactive REPL loop."""
    pt_session = skin.create_prompt_session()

    while True:
        proj_name = ""
        if s.project_path:
            proj_name = os.path.basename(s.project_path)
        elif s.is_open:
            proj_name = "(unsaved)"
        modified = s.is_modified

        try:
            line = skin.get_input(
                pt_session, project_name=proj_name, modified=modified
            ).strip()
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            elif cmd == "help":
                skin.help(REPL_COMMANDS)
            elif cmd == "status":
                result = s.status()
                _print_dict(result)
            elif cmd == "new":
                preset = args[0] if args else "letter"
                result = proj_mod.new_project(s, preset)
                skin.success(f"Created new diagram ({result['page_size']})")
            elif cmd == "open":
                if not args:
                    skin.error("Usage: open <path>")
                    continue
                result = proj_mod.open_project(s, args[0])
                skin.success(f"Opened: {args[0]}")
            elif cmd == "save":
                path = args[0] if args else None
                result = proj_mod.save_project(s, path)
                skin.success(f"Saved to: {result['path']}")
            elif cmd == "info":
                result = proj_mod.project_info(s)
                _print_dict(result)
            elif cmd == "xml":
                if not s.is_open:
                    skin.error("No project is open")
                    continue
                from cli_anything.drawio.utils.drawio_xml import xml_to_string

                click.echo(xml_to_string(s.root))
            elif cmd == "add":
                shape_type = args[0] if args else "rectangle"
                label = " ".join(args[1:]) if len(args) > 1 else ""
                result = shapes_mod.add_shape(s, shape_type, label=label)
                skin.success(f"Added {shape_type}: {result['id']}")
            elif cmd == "remove":
                if not args:
                    skin.error("Usage: remove <id>")
                    continue
                from cli_anything.drawio.utils import drawio_xml

                cell = drawio_xml.find_cell_by_id(s.root, args[0])
                if cell is None:
                    skin.error(f"Cell not found: {args[0]}")
                    continue
                s.checkpoint()
                drawio_xml.remove_cell(s.root, args[0])
                skin.success(f"Removed: {args[0]}")
            elif cmd == "shapes":
                result = shapes_mod.list_shapes(s)
                for sh in result:
                    click.echo(f"  {sh['id']}: {sh.get('value', '')} ({sh['type']})")
                skin.info(f"Total: {len(result)} shapes")
            elif cmd == "label":
                if len(args) < 2:
                    skin.error("Usage: label <id> <text>")
                    continue
                result = shapes_mod.update_label(s, args[0], " ".join(args[1:]))
                skin.success(f"Updated label: {args[0]}")
            elif cmd == "move":
                if len(args) < 3:
                    skin.error("Usage: move <id> <x> <y>")
                    continue
                result = shapes_mod.move_shape(
                    s, args[0], float(args[1]), float(args[2])
                )
                skin.success(f"Moved: {args[0]}")
            elif cmd == "resize":
                if len(args) < 3:
                    skin.error("Usage: resize <id> <width> <height>")
                    continue
                result = shapes_mod.resize_shape(
                    s, args[0], float(args[1]), float(args[2])
                )
                skin.success(f"Resized: {args[0]}")
            elif cmd == "style":
                if len(args) < 3:
                    skin.error("Usage: style <id> <key> <value>")
                    continue
                result = shapes_mod.set_style(s, args[0], args[1], args[2])
                skin.success(f"Style set: {args[1]}={args[2]}")
            elif cmd == "connect":
                if len(args) < 2:
                    skin.error("Usage: connect <source_id> <target_id> [style]")
                    continue
                edge_style = args[2] if len(args) > 2 else "orthogonal"
                result = conn_mod.add_connector(s, args[0], args[1], edge_style)
                skin.success(f"Connected: {args[0]} → {args[1]} ({result['id']})")
            elif cmd == "connectors":
                result = conn_mod.list_connectors(s)
                for e in result:
                    click.echo(
                        f"  {e['id']}: {e.get('source', '')} → {e.get('target', '')} {e.get('value', '')}"
                    )
                skin.info(f"Total: {len(result)} connectors")
            elif cmd == "pages":
                result = pages_mod.list_pages(s)
                for p in result:
                    click.echo(
                        f"  [{p['index']}] {p['name']} ({p['cell_count']} cells)"
                    )
            elif cmd == "addpage":
                name = " ".join(args) if args else ""
                result = pages_mod.add_page(s, name)
                skin.success(f"Added page: {result['name']}")
            elif cmd == "export":
                if not args:
                    skin.error("Usage: export <path> [format]")
                    continue
                fmt = args[1] if len(args) > 1 else "png"
                result = export_mod.render_or_save(s, args[0], fmt, overwrite=True)
                skin.success(
                    f"Exported to: {result.get('output', result.get('drawio_file', ''))}"
                )
            elif cmd == "undo":
                if s.undo():
                    skin.success("Undo successful")
                else:
                    skin.warning("Nothing to undo")
            elif cmd == "redo":
                if s.redo():
                    skin.success("Redo successful")
                else:
                    skin.warning("Nothing to redo")
            else:
                skin.error(
                    f"Unknown command: {cmd}. Type 'help' for available commands."
                )
        except Exception as e:
            skin.error(str(e))
