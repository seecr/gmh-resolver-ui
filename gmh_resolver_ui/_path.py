import importlib.resources as pkg_resources

__all__ = ["testdata_path", "static_path", "templates_path", "global_config_path"]

_path = pkg_resources.files("gmh_resolver_ui")
testdata_path = _path / "testdata"
static_path = _path / "static"
templates_path = _path / "templates"
global_config_path = _path / "config-data"
