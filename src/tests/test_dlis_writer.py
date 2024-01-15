import dlis_writer


def test_version() -> None:
    """Check version of the package."""

    assert dlis_writer.__version__ is not None
