# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403

# fmt: off
from .freecad_cli_p1 import get_session, output  # noqa: E402,E501
from .freecad_cli_p3 import repl  # noqa: E402,E501
# fmt: on


def handle_error(f):
    """Decorator to handle errors gracefully in CLI and REPL modes."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (
            FileNotFoundError,
            ValueError,
            IndexError,
            RuntimeError,
            FileExistsError,
            KeyError,
            TypeError,
        ) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e)}, indent=2), err=True)
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    return wrapper


def _parse_vec3(s: str) -> list[float]:
    """Parse 'x,y,z' string to [float, float, float]."""
    parts = s.split(",")
    if len(parts) != 3:
        raise ValueError(f"Expected x,y,z format, got: {s}")
    return [float(x.strip()) for x in parts]


def _parse_vec2(s: str) -> list[float]:
    """Parse 'x,y' string to [float, float]."""
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError(f"Expected x,y format, got: {s}")
    return [float(x.strip()) for x in parts]


def _parse_params(params: tuple) -> dict[str, float] | None:
    """Parse ('key=value', ...) to dict."""
    if not params:
        return None
    result = {}
    for p in params:
        if "=" not in p:
            raise ValueError(f"Param must be key=value, got: {p}")
        k, v = p.split("=", 1)
        result[k.strip()] = float(v.strip())
    return result


def _parse_indices(s: str) -> list[int]:
    """Parse comma-separated int list string '1,2,3' to [1, 2, 3]."""
    return [int(x.strip()) for x in s.split(",")]


def _parse_points(s: str) -> list[list[float]]:
    """Parse semicolon-separated points 'x,y,z;x,y,z;...' to list of vec3."""
    points = []
    for pt_str in s.split(";"):
        pt_str = pt_str.strip()
        if pt_str:
            points.append(_parse_vec3(pt_str))
    return points


def _parse_points_2d(s: str) -> list[list[float]]:
    """Parse semicolon-separated 2D points 'x,y;x,y;...' to list of vec2."""
    points = []
    for pt_str in s.split(";"):
        pt_str = pt_str.strip()
        if pt_str:
            points.append(_parse_vec2(pt_str))
    return points


def _parse_references(s: str) -> list:
    """Parse comma-separated references (ints or strings)."""
    refs = []
    for item in s.split(","):
        item = item.strip()
        try:
            refs.append(int(item))
        except ValueError:
            refs.append(item)
    return refs


output_fn = output


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output in JSON format.")
@click.option("--project", "-p", type=click.Path(), help="Load project file.")
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="Run command without saving changes to disk",
)
@click.pass_context
def cli(
    ctx: click.Context, use_json: bool, project: Optional[str], dry_run: bool
) -> None:
    """cli-anything-freecad — CLI harness for FreeCAD 3D CAD modeler."""
    global _json_output
    _json_output = use_json

    if project:
        sess = get_session()
        proj = doc_mod.open_document(project)
        sess.set_project(proj, path=project)

        # Auto-save after one-shot commands when --project is used
        def _auto_save():
            if dry_run:
                return
            if sess._modified and sess.project_path and not _repl_mode:
                sess.save_session()

        ctx.call_on_close(_auto_save)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project)
