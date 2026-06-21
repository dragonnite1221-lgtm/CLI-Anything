# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class TestBlenderRenderScriptE2E:
    """Test the render_script function directly."""

    def test_run_minimal_bpy_script(self, tmp_dir):
        """Run a minimal bpy script through Blender."""
        from cli_anything.blender.utils.blender_backend import render_script

        script_path = os.path.join(tmp_dir, "test_script.py")
        output_path = os.path.join(tmp_dir, "minimal.png")

        script_content = f'''
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cam_data = bpy.data.cameras.new(name='Camera')
cam_obj = bpy.data.objects.new('Camera', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (5, -5, 3)
cam_obj.rotation_euler = (1.1, 0, 0.8)
bpy.context.scene.camera = cam_obj
light_data = bpy.data.lights.new(name='Light', type='SUN')
light_obj = bpy.data.objects.new('Light', light_data)
bpy.context.collection.objects.link(light_obj)
bpy.context.scene.render.resolution_x = 160
bpy.context.scene.render.resolution_y = 120
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.render.filepath = r'{output_path}'
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print('Render complete')
'''
        with open(script_path, 'w') as f:
            f.write(script_content)

        result = render_script(script_path, timeout=120)
        assert result["returncode"] == 0, f"Blender failed: {result['stderr'][-500:]}"

        # Blender may append frame number
        actual_output = output_path
        if not os.path.exists(actual_output):
            base, ext = os.path.splitext(output_path)
            for suffix in ["0001", "0000"]:
                candidate = f"{base}{suffix}{ext}"
                if os.path.exists(candidate):
                    actual_output = candidate
                    break

        assert os.path.exists(actual_output), f"No output file found. stdout: {result['stdout'][-500:]}"
        size = os.path.getsize(actual_output)
        assert size > 0
        print(f"\n  Minimal render: {actual_output} ({size:,} bytes)")
