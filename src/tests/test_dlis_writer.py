import dliswriter


def test_version() -> None:
    """Check version of the package."""

    assert dliswriter.__version__ is not None
