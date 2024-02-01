import pytest

from dlis_writer.logical_record.eflr_types.file_header import FileHeaderSet, FileHeaderItem


@pytest.mark.parametrize(("header_id", "identifier", "sequence_number"), (("a", "A", 9), ("123ert", "8", 3)))
def test_creation(header_id: str, identifier: str, sequence_number: int) -> None:
    """Test creating a FileHeaderItem."""

    fh = FileHeaderItem(header_id, sequence_number=sequence_number, parent=FileHeaderSet())

    assert fh.header_id == header_id
    assert fh.sequence_number == sequence_number

    assert isinstance(fh.parent, FileHeaderSet)
    assert fh.parent.set_name is None
