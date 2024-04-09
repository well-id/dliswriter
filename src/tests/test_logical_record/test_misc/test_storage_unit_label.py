import pytest

from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer import high_compatibility_mode_decorator


@pytest.mark.parametrize(("name", "sequence_number"), (("SUL-1", 11), ("Default storage", 0)))
def test_sul_creation(name: str, sequence_number: int) -> None:
    """Test creating StorageUnitLabel."""

    sul = StorageUnitLabel(name, sequence_number=sequence_number)

    assert sul.set_identifier == name
    assert sul.sequence_number == sequence_number


@pytest.mark.parametrize("name", ("SUL-1", "UNIT1", "123-11"))
@high_compatibility_mode_decorator
def test_name_compatible(name: str) -> None:
    StorageUnitLabel(name)


@pytest.mark.parametrize("name", ("STORAGE UNIT LABEL", "SUL#12", "12.3"))
@high_compatibility_mode_decorator
def test_name_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        StorageUnitLabel(name)
