import pytest
from dlisio import dlis    # type: ignore  # untyped library


@pytest.mark.parametrize(("idx", "name", "v_zero", "m_decl", "c1_name", "c1_value", "c2_name", "c2_value"), (
        (0, "AQLN WELL-REF", "AQLN vertical_zero", 999.51, "Latitude", 40.395240, "Longitude", 27.792470),
        (1, "WRP-X", "vz20", 112.3, "X", 20, "Y", -0.3)
))
def test_well_reference_point_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, v_zero: str,
                                     m_decl: float, c1_name: str, c1_value: float, c2_name: str,
                                     c2_value: float) -> None:
    """Check attributes of well reference point in the DLIS file."""

    w = short_dlis.wellrefs[idx]

    assert w.name == name
    assert w.vertical_zero == v_zero
    assert w.magnetic_declination == m_decl
    assert w.coordinates[c1_name] == c1_value
    assert w.coordinates[c2_name] == c2_value
    assert w.origin == 42

