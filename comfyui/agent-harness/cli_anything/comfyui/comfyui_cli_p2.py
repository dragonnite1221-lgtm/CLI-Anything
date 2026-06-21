# ruff: noqa: F403, F405, E501
from .comfyui_cli_base import *  # noqa: F403

# fmt: off
from .comfyui_cli_p1 import cli, handle_error, output, workflow  # noqa: E402,E501
# fmt: on


@workflow.command("load")
@click.argument("path", type=click.Path(exists=True))
@handle_error
def workflow_load(path):
    """Load and display a workflow JSON file."""
    result = workflow_mod.load_workflow(path)
    output(result, f"Workflow: {path}")


@workflow.command("validate")
@click.argument("path", type=click.Path(exists=True))
@handle_error
def workflow_validate(path):
    """Validate the structure of a workflow JSON file."""
    wf = workflow_mod.load_workflow(path)
    result = workflow_mod.validate_workflow(wf)
    output(result, f"Validation: {path}")
    if result["valid"]:
        click.echo("  Workflow is valid.")
    else:
        click.echo(f"  {len(result['errors'])} error(s) found.", err=True)


@cli.group()
def queue():
    """Prompt queue management."""
    pass


@queue.command("prompt")
@click.option(
    "--workflow",
    "-w",
    required=True,
    type=click.Path(exists=True),
    help="Path to workflow JSON file (API format)",
)
@click.option("--client-id", default=None, help="Client ID for tracking")
@handle_error
def queue_prompt(workflow, client_id):
    """Queue a workflow for generation."""
    wf = workflow_mod.load_workflow(workflow)
    result = queue_mod.queue_prompt(_base_url, wf, client_id=client_id)
    output(result, f"Queued prompt: {result.get('prompt_id', '')}")


@queue.command("status")
@handle_error
def queue_status():
    """Show current queue status (running and pending items)."""
    result = queue_mod.get_queue_status(_base_url)
    output(result, "Queue status:")


@queue.command("clear")
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@handle_error
def queue_clear(confirm):
    """Clear all pending items from the queue."""
    if not confirm:
        click.confirm("Clear the queue?", abort=True)
    result = queue_mod.clear_queue(_base_url)
    output(result, "Queue cleared.")


@queue.command("history")
@click.option("--max-items", type=int, default=None, help="Maximum entries to show")
@handle_error
def queue_history(max_items):
    """Show completed prompt history."""
    result = queue_mod.get_history(_base_url, max_items=max_items)
    output(result, f"History ({result.get('total', 0)} entries):")


@queue.command("interrupt")
@handle_error
def queue_interrupt():
    """Stop the currently running generation."""
    result = queue_mod.interrupt(_base_url)
    output(result, "Generation interrupted.")


@cli.group()
def models():
    """Model discovery commands."""
    pass


@models.command("checkpoints")
@handle_error
def models_checkpoints():
    """List available checkpoint models."""
    result = models_mod.list_checkpoints(_base_url)
    output(result, f"Checkpoints ({len(result)}):")


@models.command("loras")
@handle_error
def models_loras():
    """List available LoRA models."""
    result = models_mod.list_loras(_base_url)
    output(result, f"LoRAs ({len(result)}):")


@models.command("vaes")
@handle_error
def models_vaes():
    """List available VAE models."""
    result = models_mod.list_vaes(_base_url)
    output(result, f"VAEs ({len(result)}):")


@models.command("controlnets")
@handle_error
def models_controlnets():
    """List available ControlNet models."""
    result = models_mod.list_controlnets(_base_url)
    output(result, f"ControlNets ({len(result)}):")


@models.command("node-info")
@click.argument("node_class")
@handle_error
def models_node_info(node_class):
    """Get input/output schema for a node class (e.g., KSampler)."""
    result = models_mod.get_node_info(_base_url, node_class)
    output(result)


@models.command("list-nodes")
@handle_error
def models_list_nodes():
    """List all available node class names."""
    result = models_mod.list_all_node_classes(_base_url)
    output(result, f"Node classes ({len(result)}):")


@cli.group()
def images():
    """Image output management."""
    pass


@images.command("list")
@click.option("--prompt-id", required=True, help="Prompt ID to list images for")
@handle_error
def images_list(prompt_id):
    """List output images for a completed prompt."""
    result = images_mod.list_output_images(_base_url, prompt_id)
    output(result, f"Output images for {prompt_id}:")
