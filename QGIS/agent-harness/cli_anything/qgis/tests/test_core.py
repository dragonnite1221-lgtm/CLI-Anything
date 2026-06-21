# ruff: noqa: F403, F405, E501
from .test_core_helpers import *  # noqa: F403


def test_project_create_save_open_and_info(tmp_path: Path):
    project_path = tmp_path / "sample.qgz"

    created = project_mod.create_project(
        str(project_path), title="Sample", crs="EPSG:4326"
    )
    assert created["path"] == str(project_path.resolve())
    assert created["title"] == "Sample"
    assert created["crs"] == "EPSG:4326"
    assert created["layer_count"] == 0
    assert created["layout_count"] == 0
    assert created["datastore_path"] == str((tmp_path / "sample_data.gpkg").resolve())

    updated = project_mod.set_project_crs("EPSG:3857")
    assert updated["crs"] == "EPSG:3857"

    saved = project_mod.save_project()
    assert Path(saved["path"]).exists()

    renamed_path = tmp_path / "renamed.qgz"
    renamed = project_mod.save_project(str(renamed_path))
    assert renamed["path"] == str(renamed_path.resolve())
    assert Path(renamed["path"]).exists()

    reopened = project_mod.open_project(str(renamed_path))
    assert reopened["path"] == str(renamed_path.resolve())
    assert reopened["crs"] == "EPSG:3857"
    assert reopened["title"] == "Sample"


def test_default_datastore_path(tmp_path: Path):
    project_path = tmp_path / "city.qgz"
    expected = tmp_path / "city_data.gpkg"
    assert project_mod.default_datastore_path(str(project_path)) == str(expected)


def test_parse_field_and_param_specs():
    fields = layers_mod.parse_field_specs(["name:string", "score:int", "active:bool"])
    assert [field["name"] for field in fields] == ["name", "score", "active"]
    assert [field["type"] for field in fields] == ["string", "integer", "bool"]

    params = processing_mod.parse_param_specs(["INPUT=areas", "DISTANCE=10"])
    assert params == ["INPUT=areas", "DISTANCE=10"]

    with pytest.raises(QgisBackendError):
        layers_mod.parse_field_specs(["name:string", "name:int"])

    with pytest.raises(QgisBackendError):
        processing_mod.parse_param_specs(["NOT_A_PARAM"])


def test_layer_create_list_info_and_remove(tmp_path: Path):
    project_mod.create_project(
        str(tmp_path / "layers.qgz"), title="Layers", crs="EPSG:4326"
    )

    created = layers_mod.create_vector_layer(
        "places",
        "point",
        "EPSG:4326",
        ["name:string", "score:int"],
    )
    assert created["name"] == "places"
    assert created["provider"] == "ogr"
    assert created["type"] == "vector"
    assert {"name", "score"}.issubset({field["name"] for field in created["fields"]})

    listing = layers_mod.list_layers()
    assert listing["count"] == 1
    assert listing["layers"][0]["name"] == "places"

    info = layers_mod.layer_info("places")
    assert info["id"] == created["id"]
    assert info["source"].endswith("layers_data.gpkg|layername=places")

    removed = layers_mod.remove_layer("places")
    assert removed["name"] == "places"
    assert layers_mod.list_layers()["count"] == 0


def test_feature_add_and_list(tmp_path: Path):
    project_mod.create_project(
        str(tmp_path / "features.qgz"), title="Features", crs="EPSG:4326"
    )
    layers_mod.create_vector_layer(
        "points",
        "point",
        "EPSG:4326",
        ["name:string", "count:int", "rating:double", "active:bool"],
    )

    added = features_mod.add_feature(
        "points",
        "POINT(1 2)",
        ["name=HQ", "count=7", "rating=2.5", "active=true"],
    )
    attrs = added["feature"]["attributes"]
    assert attrs["name"] == "HQ"
    assert attrs["count"] == 7
    assert float(attrs["rating"]) == pytest.approx(2.5)
    assert bool(attrs["active"]) is True

    listing = features_mod.list_features("points", limit=1)
    assert listing["feature_count"] == 1
    assert len(listing["features"]) == 1
    assert listing["features"][0]["geometry_wkt"].startswith("Point")


def test_feature_add_rejects_invalid_boolean(tmp_path: Path):
    project_mod.create_project(
        str(tmp_path / "invalid_bool.qgz"), title="InvalidBool", crs="EPSG:4326"
    )
    layers_mod.create_vector_layer("points", "point", "EPSG:4326", ["active:bool"])

    with pytest.raises(QgisBackendError):
        features_mod.add_feature("points", "POINT(0 0)", ["active=maybe"])
