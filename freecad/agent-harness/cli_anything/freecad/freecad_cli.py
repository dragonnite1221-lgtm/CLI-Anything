# ruff: noqa: F403, F405, E501
from .freecad_cli_base import *  # noqa: F403
from .freecad_cli_p42 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .freecad_cli_p1 import get_session, output, _spawn_live_viewer, _spawn_live_poller  # noqa: F401,E501
from .freecad_cli_p10 import sketch_add_bspline, sketch_add_slot, sketch_edit_element, sketch_remove_element, sketch_remove_constraint, sketch_edit_constraint, sketch_mirror  # noqa: F401,E501
from .freecad_cli_p11 import sketch_offset, sketch_trim, sketch_extend, sketch_validate, sketch_solve_status, sketch_set_construction, sketch_project_external, sketch_intersection, sketch_add_external_face  # noqa: F401,E501
from .freecad_cli_p12 import body_group, body_new, body_pad, body_pocket, body_fillet, body_chamfer, body_revolution, body_list, body_get  # noqa: F401,E501
from .freecad_cli_p13 import body_groove, body_additive_loft, body_additive_pipe, body_additive_helix, body_subtractive_loft, body_subtractive_pipe, body_subtractive_helix  # noqa: F401,E501
from .freecad_cli_p14 import body_additive_box, body_additive_cylinder, body_additive_sphere, body_additive_cone  # noqa: F401,E501
from .freecad_cli_p15 import body_additive_torus, body_additive_wedge, body_subtractive_box, body_subtractive_cylinder  # noqa: F401,E501
from .freecad_cli_p16 import body_subtractive_sphere, body_subtractive_cone, body_subtractive_torus, body_subtractive_wedge  # noqa: F401,E501
from .freecad_cli_p17 import body_draft_feature, body_thickness_feature, body_hole, body_linear_pattern, body_polar_pattern, body_mirrored  # noqa: F401,E501
from .freecad_cli_p18 import body_multi_transform, body_datum_plane, body_datum_line, body_datum_point, body_shape_binder, body_local_coordinate_system  # noqa: F401,E501
from .freecad_cli_p19 import body_toggle_freeze, material_group, material_create, material_assign, material_list, material_get, material_set, material_presets, material_import  # noqa: F401,E501
from .freecad_cli_p2 import handle_error, _parse_vec3, _parse_vec2, _parse_params, _parse_indices, _parse_points, _parse_points_2d, _parse_references, output_fn, cli  # noqa: F401,E501
from .freecad_cli_p20 import material_export, export_group, export_render, export_info, export_presets, preview_group, preview_live_group, preview_recipes, preview_capture, preview_latest  # noqa: F401,E501
from .freecad_cli_p21 import preview_live_start, preview_live_push, preview_live_status, preview_live_stop, preview_live_monitor, motion_group  # noqa: F401,E501
from .freecad_cli_p22 import motion_new, motion_list, motion_get, motion_delete, motion_keyframe, motion_sample  # noqa: F401,E501
from .freecad_cli_p23 import motion_render_frames, motion_render_video, session_group, session_undo, session_redo  # noqa: F401,E501
from .freecad_cli_p24 import session_status, session_history, measure_group, measure_distance, measure_length, measure_angle, measure_area, measure_volume, measure_radius, measure_diameter, measure_position, measure_center_of_mass  # noqa: F401,E501
from .freecad_cli_p25 import measure_bounding_box, measure_inertia, measure_check_geometry, spreadsheet_group, spreadsheet_new, spreadsheet_set_cell, spreadsheet_get_cell, spreadsheet_set_alias, spreadsheet_import_csv, spreadsheet_export_csv  # noqa: F401,E501
from .freecad_cli_p26 import spreadsheet_list, mesh_group, mesh_import, mesh_from_shape, mesh_export, mesh_info, mesh_analyze, mesh_check, mesh_boolean, mesh_decimate  # noqa: F401,E501
from .freecad_cli_p27 import mesh_remesh, mesh_smooth, mesh_repair, mesh_fill_holes, mesh_flip_normals, mesh_merge, mesh_split, mesh_to_shape, draft_group, draft_wire  # noqa: F401,E501
from .freecad_cli_p28 import draft_rectangle, draft_circle, draft_ellipse, draft_polygon, draft_bspline, draft_bezier, draft_point  # noqa: F401,E501
from .freecad_cli_p29 import draft_text, draft_shapestring, draft_dimension, draft_label, draft_hatch, draft_move, draft_rotate  # noqa: F401,E501
from .freecad_cli_p3 import repl, document_group, document_new  # noqa: F401,E501
from .freecad_cli_p30 import draft_scale, draft_mirror, draft_offset, draft_array_linear, draft_array_polar, draft_array_path, draft_copy  # noqa: F401,E501
from .freecad_cli_p31 import draft_clone, draft_upgrade, draft_downgrade, draft_trim, draft_join, draft_extrude, draft_fillet_2d, draft_to_sketch, draft_list, draft_get  # noqa: F401,E501
from .freecad_cli_p32 import draft_remove, surface_group, surface_filling, surface_sections, surface_extend, surface_blend_curve, surface_sew, surface_cut, import_group  # noqa: F401,E501
from .freecad_cli_p33 import import_auto, import_step, import_iges, import_stl, import_obj, import_dxf, import_svg, import_brep, import_3mf  # noqa: F401,E501
from .freecad_cli_p34 import import_ply, import_off, import_gltf, import_info, assembly_group, assembly_new, assembly_add_part, assembly_remove_part, assembly_list, assembly_get  # noqa: F401,E501
from .freecad_cli_p35 import assembly_constrain, assembly_solve, assembly_dof, assembly_bom, assembly_explode, assembly_collapse, assembly_insert_part, assembly_create_simulation  # noqa: F401,E501
from .freecad_cli_p36 import assembly_add_sim_step, techdraw_group, techdraw_new_page, techdraw_set_template, techdraw_add_view, techdraw_add_projection_group, techdraw_add_section_view, techdraw_add_detail_view  # noqa: F401,E501
from .freecad_cli_p37 import techdraw_add_dimension, techdraw_add_annotation, techdraw_add_leader, techdraw_add_centerline, techdraw_add_hatch, techdraw_export_pdf, techdraw_export_svg, techdraw_list_views  # noqa: F401,E501
from .freecad_cli_p38 import techdraw_get_view, fem_group, fem_new_analysis, fem_add_fixed, fem_add_force, fem_add_pressure, fem_add_displacement, fem_add_temperature, fem_add_heatflux  # noqa: F401,E501
from .freecad_cli_p39 import fem_set_material, fem_mesh_generate, fem_solve, fem_results, fem_export_results, fem_add_beam_section  # noqa: F401,E501
from .freecad_cli_p4 import document_open, document_save, document_info, document_profiles, part_group, part_add, part_remove, part_list, part_get, part_transform  # noqa: F401,E501
from .freecad_cli_p40 import fem_add_tie, fem_purge_results, fem_suppress, cam_group, cam_new_job, cam_set_stock, cam_add_profile, cam_add_pocket  # noqa: F401,E501
from .freecad_cli_p41 import cam_add_drilling, cam_add_facing, cam_set_tool, cam_generate_gcode, cam_simulate, cam_export_gcode, cam_add_tapping, cam_import_tool_library  # noqa: F401,E501
from .freecad_cli_p42 import cam_export_tool_library  # noqa: F401,E501
from .freecad_cli_p5 import part_boolean, part_copy, part_mirror, part_scale, part_offset, part_thickness, part_compound, part_explode  # noqa: F401,E501
from .freecad_cli_p6 import part_fillet_3d, part_chamfer_3d, part_loft, part_sweep, part_revolve, part_extrude, part_section  # noqa: F401,E501
from .freecad_cli_p7 import part_slice, part_line_3d, part_wire, part_polygon_3d, part_info, part_bounds  # noqa: F401,E501
from .freecad_cli_p8 import part_align, sketch_group, sketch_new, sketch_add_line, sketch_add_circle, sketch_add_rect  # noqa: F401,E501
from .freecad_cli_p9 import sketch_add_arc, sketch_constrain, sketch_close, sketch_list, sketch_get, sketch_add_point, sketch_add_ellipse, sketch_add_polygon  # noqa: F401,E501
# fmt: on
