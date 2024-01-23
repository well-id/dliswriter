import pytest

from dlis_writer.logical_record.eflr_types.file_header import FileHeaderSet, FileHeaderItem


@pytest.mark.parametrize(("identifier", "sequence_number"), (("a", 9), ("123ert", 3)))
def test_creation(identifier: str, sequence_number: int) -> None:
    """Test creating a FileHeaderObject."""

    fh = FileHeaderItem(identifier, sequence_number=sequence_number, parent=FileHeaderSet())

    assert fh.identifier == identifier
    assert fh.sequence_number == sequence_number

    assert isinstance(fh.parent, FileHeaderSet)
    assert fh.parent.set_name is None
