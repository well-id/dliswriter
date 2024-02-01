import pytest
from dlisio import dlis    # type: ignore  # untyped library


def test_equipment(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Equipment objects in the DLIS file matches the expected one."""

    eq = short_dlis.equipments
    assert len(eq) == 3


@pytest.mark.parametrize(("idx", "name", "status", "serial_number"), (
        (0, "EQ1", 1, "9101-21391"),
        (1, "EQ2", 0, "5559101-21391"),
        (2, "EqX", 1, "12311")
))
def test_equipment_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, status: int,
                          serial_number: str) -> None:
    eq = short_dlis.equipments[idx]

    assert eq.name == name
    assert eq.status == status
    assert eq.serial_number == serial_number
    assert eq.origin == 42
