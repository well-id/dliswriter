import pytest

from dlis_writer.logical_record.misc import StorageUnitLabel


@pytest.mark.parametrize(("name", "sequence_number"), (("SUL-1", 11), ("Default storage", 0)))
def test_sul_creation(name: str, sequence_number: int):
    """Test creating StorageUnitLabel."""

    sul = StorageUnitLabel(name, sequence_number=sequence_number)

    assert sul.set_identifier == name
    assert sul.sequence_number == sequence_number
