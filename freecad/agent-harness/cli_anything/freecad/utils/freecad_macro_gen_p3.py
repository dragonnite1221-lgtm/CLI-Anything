# ruff: noqa: F403, F405, E501
from .freecad_macro_gen_base import *  # noqa: F403
# fmt: off
from .freecad_macro_gen_p1 import _safe_name  # noqa: E402,E501
from .freecad_macro_gen_p2 import _dominant_axis, _gen_bodies_header, _placement_expr  # noqa: E402,E501
# fmt: on


def _gen_bodies(project: dict) -> List[str]:
    """Generate PartDesign bodies with primitive and pattern features."""
    lines: List[str] = []
    bodies = project.get("bodies", [])

    if not bodies:
        return lines

    lines.append("import PartDesign")
    lines.append("")
    _gen_bodies_header(lines)

    for body in bodies:
        body_name = _safe_name(body.get("name", "Body"))
        body_var = f"body_{body_name}"
        lines.append(f"{body_var} = doc.addObject('PartDesign::Body', '{body_name}')")

        features = body.get("features", [])
        previous_var: Optional[str] = None
        feature_counter = 0

        def emit_pattern(
            pattern_type: str,
            pattern_payload: Dict[str, Any],
            source_var: Optional[str],
            suffix: Optional[str] = None,
        ) -> Optional[str]:
            nonlocal feature_counter
            if source_var is None:
                lines.append(f"# WARNING: Cannot add {pattern_type} without a previous body feature")
                return None
            feature_counter += 1
            pattern_var = f"feat_{body_name}_{feature_counter}_{pattern_type}"
            label = _safe_name(f"{pattern_type}_{feature_counter}")
            if pattern_type == "linear_pattern":
                axis, reversed_axis, off_axis = _dominant_axis(pattern_payload.get("direction"))
                lines.append(
                    f"{pattern_var} = {body_var}.newObject('PartDesign::LinearPattern', '{label}')"
                )
                lines.append(f"{pattern_var}.Originals = [{source_var}]")
                lines.append(
                    f"{pattern_var}.Direction = (_body_origin_ref({body_var}, '{axis}_Axis'), [''])"
                )
                lines.append(f"{pattern_var}.Length = {float(pattern_payload.get('length', 50.0))}")
                lines.append(
                    f"{pattern_var}.Occurrences = {int(pattern_payload.get('occurrences', 3))}"
                )
                if reversed_axis:
                    lines.append(f"{pattern_var}.Reversed = True")
                if off_axis:
                    lines.append(
                        f"# WARNING: Non-axis-aligned direction {pattern_payload.get('direction')} "
                        f"collapsed to dominant {axis}-axis"
                    )
            elif pattern_type == "polar_pattern":
                axis = str(pattern_payload.get("axis", "Z")).upper()
                lines.append(
                    f"{pattern_var} = {body_var}.newObject('PartDesign::PolarPattern', '{label}')"
                )
                lines.append(f"{pattern_var}.Originals = [{source_var}]")
                lines.append(
                    f"{pattern_var}.Axis = (_body_origin_ref({body_var}, '{axis}_Axis'), [''])"
                )
                lines.append(f"{pattern_var}.Angle = {float(pattern_payload.get('angle', 360.0))}")
                lines.append(
                    f"{pattern_var}.Occurrences = {int(pattern_payload.get('occurrences', 4))}"
                )
            elif pattern_type == "mirrored":
                plane = str(pattern_payload.get("plane", "XY")).upper()
                lines.append(
                    f"{pattern_var} = {body_var}.newObject('PartDesign::Mirrored', '{label}')"
                )
                lines.append(f"{pattern_var}.Originals = [{source_var}]")
                lines.append(
                    f"{pattern_var}.MirrorPlane = (_body_origin_ref({body_var}, '{plane}_Plane'), [''])"
                )
            else:
                lines.append(f"# WARNING: Unknown pattern type '{pattern_type}' in {suffix or 'feature'}")
                return source_var
            lines.append("")
            return pattern_var

        primitive_map = {
            "additive_box": ("PartDesign::AdditiveBox", ("Length", "length"), ("Width", "width"), ("Height", "height")),
            "additive_cylinder": ("PartDesign::AdditiveCylinder", ("Radius", "radius"), ("Height", "height")),
            "additive_sphere": ("PartDesign::AdditiveSphere", ("Radius", "radius")),
            "additive_cone": ("PartDesign::AdditiveCone", ("Radius1", "radius1"), ("Radius2", "radius2"), ("Height", "height")),
            "additive_torus": ("PartDesign::AdditiveTorus", ("Radius1", "radius1"), ("Radius2", "radius2")),
            "additive_wedge": ("PartDesign::AdditiveWedge", ("Xmin", "xmin"), ("Xmax", "xmax"), ("Ymin", "ymin"), ("Ymax", "ymax"), ("Zmin", "zmin"), ("Zmax", "zmax"), ("X2min", "x2min"), ("X2max", "x2max"), ("Z2min", "z2min"), ("Z2max", "z2max")),
            "subtractive_box": ("PartDesign::SubtractiveBox", ("Length", "length"), ("Width", "width"), ("Height", "height")),
            "subtractive_cylinder": ("PartDesign::SubtractiveCylinder", ("Radius", "radius"), ("Height", "height")),
            "subtractive_sphere": ("PartDesign::SubtractiveSphere", ("Radius", "radius")),
            "subtractive_cone": ("PartDesign::SubtractiveCone", ("Radius1", "radius1"), ("Radius2", "radius2"), ("Height", "height")),
            "subtractive_torus": ("PartDesign::SubtractiveTorus", ("Radius1", "radius1"), ("Radius2", "radius2")),
            "subtractive_wedge": ("PartDesign::SubtractiveWedge", ("Xmin", "xmin"), ("Xmax", "xmax"), ("Ymin", "ymin"), ("Ymax", "ymax"), ("Zmin", "zmin"), ("Zmax", "zmax"), ("X2min", "x2min"), ("X2max", "x2max"), ("Z2min", "z2min"), ("Z2max", "z2max")),
        }

        for feat in features:
            feat_type = feat.get("type", "pad").lower()
            feat_name = _safe_name(feat.get("name", f"Feature_{feat_type}"))
            feat_props = feat.get("properties", {})
            feature_counter += 1
            feat_var = f"feat_{body_name}_{feature_counter}_{_safe_name(feat_type)}"

            if feat_type in primitive_map:
                class_name, *prop_pairs = primitive_map[feat_type]
                lines.append(f"{feat_var} = {body_var}.newObject('{class_name}', '{feat_name}')")
                for prop_name, key in prop_pairs:
                    value = feat.get(key, feat_props.get(key))
                    if value is not None:
                        lines.append(f"{feat_var}.{prop_name} = {float(value)}")
                placement_expr = _placement_expr(feat.get("placement") or feat_props.get("placement"))
                if placement_expr:
                    lines.append(f"{feat_var}.Placement = {placement_expr}")
                previous_var = feat_var

            elif feat_type == "linear_pattern":
                previous_var = emit_pattern("linear_pattern", feat, previous_var)

            elif feat_type == "polar_pattern":
                previous_var = emit_pattern("polar_pattern", feat, previous_var)

            elif feat_type == "mirrored":
                previous_var = emit_pattern("mirrored", feat, previous_var)

            elif feat_type == "multi_transform":
                transforms = feat.get("transformations", [])
                if not transforms:
                    lines.append(f"# WARNING: multi_transform '{feat_name}' has no transformations")
                for transform_index, transform in enumerate(transforms):
                    previous_var = emit_pattern(
                        str(transform.get("type", "")).lower(),
                        transform,
                        previous_var,
                        suffix=f"multi_transform[{transform_index}]",
                    )

            elif feat_type == "pad":
                length = feat_props.get("length", feat_props.get("Length", 10.0))
                lines.append(
                    f"{feat_var} = {body_var}.newObject('PartDesign::Pad', '{feat_name}')"
                )
                lines.append(f"{feat_var}.Length = {length}")
                previous_var = feat_var

            elif feat_type == "pocket":
                length = feat_props.get("length", feat_props.get("Length", 5.0))
                lines.append(
                    f"{feat_var} = {body_var}.newObject('PartDesign::Pocket', '{feat_name}')"
                )
                lines.append(f"{feat_var}.Length = {length}")
                previous_var = feat_var

            elif feat_type == "revolution":
                angle = feat_props.get("angle", feat_props.get("Angle", 360.0))
                lines.append(
                    f"{feat_var} = {body_var}.newObject('PartDesign::Revolution', '{feat_name}')"
                )
                lines.append(f"{feat_var}.Angle = {angle}")
                previous_var = feat_var

            elif feat_type == "chamfer":
                size = feat_props.get("size", feat_props.get("Size", 1.0))
                lines.append(
                    f"{feat_var} = {body_var}.newObject('PartDesign::Chamfer', '{feat_name}')"
                )
                lines.append(f"{feat_var}.Size = {size}")
                previous_var = feat_var

            elif feat_type == "fillet":
                radius = feat_props.get("radius", feat_props.get("Radius", 1.0))
                lines.append(
                    f"{feat_var} = {body_var}.newObject('PartDesign::Fillet', '{feat_name}')"
                )
                lines.append(f"{feat_var}.Radius = {radius}")
                previous_var = feat_var

            else:
                lines.append(
                    f"# WARNING: Unknown feature type '{feat_type}' "
                    f"for '{feat_name}'"
                )

            lines.append("")

    return lines
