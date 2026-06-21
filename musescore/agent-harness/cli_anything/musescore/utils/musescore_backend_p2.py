# ruff: noqa: F403, F405, E501
from .musescore_backend_base import *  # noqa: F403

# fmt: off
from .musescore_backend_p1 import run_mscore  # noqa: E402,E501
# fmt: on


def export_score(
    input_path: str,
    output_path: str,
    *,
    dpi: int | None = None,
    bitrate: int | None = None,
    trim: int | None = None,
    style: str | None = None,
    sound_profile: str | None = None,
    export_parts: bool = False,
) -> Path:
    """Export a score to the specified format via mscore -o.

    Format is inferred from the output file extension.

    Args:
        input_path: Path to input score (.mscz, .mxl, .mid).
        output_path: Path to output file (extension determines format).
        dpi: PNG resolution in DPI.
        bitrate: MP3 bitrate in kbps.
        trim: PNG/SVG whitespace trim margin.
        style: Path to .mss style file to apply.
        sound_profile: Audio profile ("MuseScore Basic" or "Muse Sounds").
        export_parts: Whether to append parts to PDF export.

    Returns:
        Path to the output file.
    """
    args = []

    if style:
        args.extend(["-S", style])
    if dpi is not None:
        args.extend(["-r", str(dpi)])
    if bitrate is not None:
        args.extend(["-b", str(bitrate)])
    if trim is not None:
        args.extend(["-T", str(trim)])
    if sound_profile:
        args.extend(["--sound-profile", sound_profile])
    if export_parts:
        args.append("-P")

    args.extend(["-o", str(output_path), str(input_path)])
    run_mscore(args)

    return Path(output_path)


def transpose_score(input_path: str, output_path: str, transpose_opts: dict) -> Path:
    """Transpose a score and save the result.

    Args:
        input_path: Path to input score.
        output_path: Path to output score.
        transpose_opts: Transpose options dict with keys:
            mode, direction, targetKey, transposeInterval,
            transposeKeySignatures, transposeChordNames,
            useDoubleSharpsFlats.

    Returns:
        Path to the output file.
    """
    opts_json = json.dumps(transpose_opts)
    args = ["--transpose", opts_json, "-o", str(output_path), str(input_path)]
    run_mscore(args)
    return Path(output_path)


def get_score_meta(input_path: str) -> dict:
    """Get score metadata via --score-meta.

    Returns parsed JSON with title, composer, keysig, timesig,
    tempo, duration, measures, pages, parts, etc.
    The raw output wraps everything in a "metadata" key; we unwrap it.
    """
    result = run_mscore(["--score-meta", str(input_path)])
    data = json.loads(result.stdout)
    # Unwrap the outer "metadata" envelope if present
    if "metadata" in data and isinstance(data["metadata"], dict):
        return data["metadata"]
    return data


def get_score_parts(input_path: str) -> dict:
    """Get score parts via --score-parts.

    Returns parsed JSON with part names and base64-encoded .mscz data.
    """
    result = run_mscore(["--score-parts", str(input_path)])
    return json.loads(result.stdout)


def get_score_media(input_path: str) -> dict:
    """Get all score media via --score-media.

    Returns parsed JSON with pngs, svgs, pdf, midi, mxml, metadata, etc.
    """
    result = run_mscore(["--score-media", str(input_path)])
    return json.loads(result.stdout)


def diff_scores(file_a: str, file_b: str, raw: bool = False) -> dict:
    """Diff two scores.

    Args:
        file_a: Path to first score.
        file_b: Path to second score.
        raw: If True, use --raw-diff instead of --diff.

    Returns:
        Parsed JSON diff result.
    """
    flag = "--raw-diff" if raw else "--diff"
    result = run_mscore([flag, str(file_a), str(file_b)])
    return json.loads(result.stdout)


def batch_convert(job_list: list[dict]) -> list[Path]:
    """Run batch conversion via mscore -j.

    Args:
        job_list: List of dicts with "in" and "out" keys.

    Returns:
        List of output paths.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(job_list, f)
        job_file = f.name

    try:
        run_mscore(["-j", job_file])
    finally:
        os.unlink(job_file)

    return [Path(job["out"]) for job in job_list]
