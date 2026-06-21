# ruff: noqa: F403, F405, E501
from .comfyui_cli_base import *  # noqa: F403

# fmt: off
from .comfyui_cli_p1 import cli, handle_error, output  # noqa: E402,E501
from .comfyui_cli_p2 import images  # noqa: E402,E501
# fmt: on


@images.command("download")
@click.option(
    "--filename", required=True, help="Image filename (e.g., ComfyUI_00001_.png)"
)
@click.option(
    "--output",
    "output_path",
    required=True,
    type=click.Path(),
    help="Local path to save the image",
)
@click.option("--subfolder", default="", help="Subfolder in ComfyUI output dir")
@click.option(
    "--type",
    "image_type",
    default="output",
    type=click.Choice(["output", "input", "temp"]),
    help="Image type",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing file")
@handle_error
def images_download(filename, output_path, subfolder, image_type, overwrite):
    """Download a single output image from ComfyUI."""
    result = images_mod.download_image(
        base_url=_base_url,
        filename=filename,
        output_path=output_path,
        subfolder=subfolder,
        image_type=image_type,
        overwrite=overwrite,
    )
    output(result, f"Downloaded: {output_path}")


@images.command("download-all")
@click.option("--prompt-id", required=True, help="Prompt ID to download images for")
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(),
    help="Directory to save images into",
)
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
@handle_error
def images_download_all(prompt_id, output_dir, overwrite):
    """Download all output images for a prompt to a directory."""
    result = images_mod.download_prompt_images(
        base_url=_base_url,
        prompt_id=prompt_id,
        output_dir=output_dir,
        overwrite=overwrite,
    )
    output(result, f"Downloaded {len(result)} image(s) to {output_dir}")


@cli.group()
def system():
    """System information commands."""
    pass


@system.command("stats")
@handle_error
def system_stats():
    """Show GPU/memory system stats."""
    result = api_get(_base_url, "/system_stats")
    output(result, "System stats:")


@system.command("info")
@handle_error
def system_info():
    """Show ComfyUI server information."""
    result = api_get(_base_url, "/")
    output(result, "Server info:")


def main():
    cli()
