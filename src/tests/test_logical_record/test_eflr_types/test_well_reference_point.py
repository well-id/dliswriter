import pytest

from dliswriter.logical_record.eflr_types.well_reference_point import WellReferencePointSet, WellReferencePointItem


@pytest.mark.parametrize(("name", "v_zero", "m_decl", "c1_name", "c1_value", "c2_name", "c2_value"), (
        ("AQLN WELL-REF", "AQLN vertical_zero", 999.51, "Latitude", 40.395240, "Longitude", 27.792470),
        ("WRP-X", "vz20", 112.3, "X", 20, "Y", -0.3)
))
def test_from_config(name: str, v_zero: str, m_decl: float, c1_name: str, c1_value: float, c2_name: str,
                     c2_value: float) -> None:
    """Test creating WellReferencePointItem."""

    w = WellReferencePointItem(
        name,
        vertical_zero=v_zero,
        magnetic_declination=m_decl,
        coordinate_1_name=c1_name,
        coordinate_1_value=c1_value,
        coordinate_2_name=c2_name,
        coordinate_2_value=c2_value,
        parent=WellReferencePointSet()
    )

    assert w.name == name
    assert w.vertical_zero.value == v_zero
    assert w.magnetic_declination.value == m_decl
    assert w.coordinate_1_name.value == c1_name
    assert w.coordinate_1_value.value == c1_value
    assert w.coordinate_2_name.value == c2_name
    assert w.coordinate_2_value.value == c2_value

    assert isinstance(w.parent, WellReferencePointSet)
    assert w.parent.set_name is None
