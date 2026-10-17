from importlib.metadata import version

import tensemem


def test_version_matches_installed_metadata() -> None:
    assert tensemem.__version__ == version("tensemem")
