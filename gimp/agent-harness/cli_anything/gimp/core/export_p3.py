# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p2 import _apply_sepia  # noqa: E402,E501
# fmt: on


def _apply_single_filter(img, name, params):
    """Apply a single filter to an image (Pillow fallback path)."""
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    from cli_anything.gimp.core.filters import FILTER_REGISTRY

    if name not in FILTER_REGISTRY:
        return img

    spec = FILTER_REGISTRY[name]
    engine = spec["engine"]

    needs_rgba = img.mode == "RGBA"

    if engine == "pillow_enhance":
        cls_name = spec["pillow_class"]
        factor = params.get("factor", 1.0)
        if needs_rgba:
            alpha = img.split()[3]
            rgb = img.convert("RGB")
            enhancer = getattr(ImageEnhance, cls_name)(rgb)
            result = enhancer.enhance(factor).convert("RGBA")
            result.putalpha(alpha)
            return result
        else:
            enhancer = getattr(ImageEnhance, cls_name)(img)
            return enhancer.enhance(factor)

    elif engine == "pillow_ops":
        func_name = spec["pillow_func"]
        if needs_rgba:
            alpha = img.split()[3]
            rgb = img.convert("RGB")
        else:
            rgb = img

        if func_name == "autocontrast":
            result = ImageOps.autocontrast(rgb, cutoff=params.get("cutoff", 0))
        elif func_name == "equalize":
            result = ImageOps.equalize(rgb)
        elif func_name == "invert":
            result = ImageOps.invert(rgb)
        elif func_name == "posterize":
            result = ImageOps.posterize(rgb, bits=params.get("bits", 4))
        elif func_name == "solarize":
            result = ImageOps.solarize(rgb, threshold=params.get("threshold", 128))
        elif func_name == "grayscale":
            result = ImageOps.grayscale(rgb)
            if needs_rgba:
                result = result.convert("RGBA")
                result.putalpha(alpha)
                return result
            return result
        else:
            return img

        if needs_rgba:
            result = result.convert("RGBA")
            result.putalpha(alpha)
        return result

    elif engine == "pillow_filter":
        filter_name = spec["pillow_filter"]
        if filter_name == "GaussianBlur":
            pf = ImageFilter.GaussianBlur(radius=params.get("radius", 2.0))
        elif filter_name == "BoxBlur":
            pf = ImageFilter.BoxBlur(radius=params.get("radius", 2.0))
        elif filter_name == "UnsharpMask":
            pf = ImageFilter.UnsharpMask(
                radius=params.get("radius", 2.0),
                percent=params.get("percent", 150),
                threshold=params.get("threshold", 3),
            )
        elif filter_name == "SMOOTH_MORE":
            pf = ImageFilter.SMOOTH_MORE
        elif filter_name == "FIND_EDGES":
            pf = ImageFilter.FIND_EDGES
        elif filter_name == "EMBOSS":
            pf = ImageFilter.EMBOSS
        elif filter_name == "CONTOUR":
            pf = ImageFilter.CONTOUR
        elif filter_name == "DETAIL":
            pf = ImageFilter.DETAIL
        else:
            return img
        return img.filter(pf)

    elif engine == "pillow_transform":
        method = spec["pillow_method"]
        if method == "rotate":
            angle = params.get("angle", 0.0)
            expand = params.get("expand", True)
            return img.rotate(-angle, expand=expand, resample=Image.BICUBIC)
        elif method == "flip_h":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        elif method == "flip_v":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        elif method == "resize":
            w = params.get("width", img.width)
            h = params.get("height", img.height)
            resample_map = {
                "nearest": Image.NEAREST,
                "bilinear": Image.BILINEAR,
                "bicubic": Image.BICUBIC,
                "lanczos": Image.LANCZOS,
            }
            rs = resample_map.get(params.get("resample", "lanczos"), Image.LANCZOS)
            return img.resize((w, h), rs)
        elif method == "crop":
            left = params.get("left", 0)
            top = params.get("top", 0)
            right = params.get("right", img.width)
            bottom = params.get("bottom", img.height)
            return img.crop((left, top, right, bottom))

    elif engine == "custom":
        func_name = spec["custom_func"]
        if func_name == "apply_sepia":
            return _apply_sepia(img, params.get("strength", 0.8))

    return img
