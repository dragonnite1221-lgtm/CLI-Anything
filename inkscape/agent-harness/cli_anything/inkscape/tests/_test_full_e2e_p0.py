# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset the ID counter before each test."""
    reset_id_counter()


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d
