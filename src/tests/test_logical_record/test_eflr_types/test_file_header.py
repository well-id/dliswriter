import pytest

from dliswriter.logical_record.eflr_types.file_header import FileHeaderSet, FileHeaderItem
from dliswriter import high_compatibility_mode_decorator


@pytest.mark.parametrize(("header_id", "identifier", "sequence_number"), (("a", "A", 9), ("123ert", "8", 3)))
def test_creation(header_id: str, identifier: str, sequence_number: int) -> None:
    """Test creating a FileHeaderItem."""

    fh = FileHeaderItem(header_id, sequence_number=sequence_number, parent=FileHeaderSet())

    assert fh.header_id == header_id
    assert fh.sequence_number == sequence_number

    assert isinstance(fh.parent, FileHeaderSet)
    assert fh.parent.set_name is None


@pytest.mark.parametrize("name", ("FH-1", "DEFAULT_FILE_HEADER", "12-3"))
@high_compatibility_mode_decorator
def test_header_id_compatible(name: str) -> None:
    FileHeaderItem(name, parent=FileHeaderSet())


@pytest.mark.parametrize("name", ("Fh1", "file.header", "fh 8"))
@high_compatibility_mode_decorator
def test_header_id_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        FileHeaderItem(name, parent=FileHeaderSet())
