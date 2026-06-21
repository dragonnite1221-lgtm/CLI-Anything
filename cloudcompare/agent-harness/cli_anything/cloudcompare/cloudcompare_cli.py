# ruff: noqa: F403, F405, E501
from .cloudcompare_cli_base import *  # noqa: F403
from .cloudcompare_cli_p17 import main  # noqa: F401


if __name__ == "__main__":
    main()

# fmt: off
# re-export full surface
from .cloudcompare_cli_p1 import _pretty, _out, _error, _require_project, cli  # noqa: F401,E501
from .cloudcompare_cli_p10 import cloud_sf_filter_z, cloud_sf_to_rgb, cloud_rgb_to_sf  # noqa: F401,E501
from .cloudcompare_cli_p11 import cloud_noise_filter, cloud_invert_normals, cloud_segment_cc  # noqa: F401,E501
from .cloudcompare_cli_p12 import cloud_mesh_delaunay, cloud_merge, cloud_convert, distance  # noqa: F401,E501
from .cloudcompare_cli_p13 import distance_c2c, distance_c2m, transform  # noqa: F401,E501
from .cloudcompare_cli_p14 import transform_icp, transform_apply, mesh  # noqa: F401,E501
from .cloudcompare_cli_p15 import mesh_add, mesh_list, mesh_sample, export, export_cloud_cmd  # noqa: F401,E501
from .cloudcompare_cli_p16 import export_mesh_cmd, export_batch, export_formats, session_group, session_save, session_history, session_undo  # noqa: F401,E501
from .cloudcompare_cli_p17 import session_set_format, info_cmd  # noqa: F401,E501
from .cloudcompare_cli_p2 import repl, project  # noqa: F401,E501
from .cloudcompare_cli_p3 import project_new, project_info_cmd, project_status, cloud, cloud_add, cloud_list  # noqa: F401,E501
from .cloudcompare_cli_p4 import cloud_subsample, cloud_roughness  # noqa: F401,E501
from .cloudcompare_cli_p5 import cloud_density, cloud_curvature  # noqa: F401,E501
from .cloudcompare_cli_p6 import cloud_normals, cloud_filter_sor  # noqa: F401,E501
from .cloudcompare_cli_p7 import cloud_crop  # noqa: F401,E501
from .cloudcompare_cli_p8 import cloud_filter_csf  # noqa: F401,E501
from .cloudcompare_cli_p9 import cloud_sf_from_coord, cloud_filter_sf  # noqa: F401,E501
# fmt: on
