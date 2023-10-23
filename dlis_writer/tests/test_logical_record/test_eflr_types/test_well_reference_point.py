import pytest

from dlis_writer.logical_record.eflr_types import WellReferencePoint
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.mark.parametrize(("key", "name", "v_zero", "m_decl", "c1_name", "c1_value", "c2_name", "c2_value"), (
        ("1", "AQLN WELL-REF", "AQLN vertical_zero", 999.51, "Latitude", 40.395240, "Longitude", 27.792470),
        ("X", "WRP-X", "vz20", 112.3, "X", 20, "Y", -0.3)
))
def test_from_config(config_params, key, name, v_zero, m_decl, c1_name, c1_value, c2_name, c2_value):
    key = f"WellReferencePoint-{key}"
    w = WellReferencePoint.make_from_config(config_params, key=key)

    assert w.name == name
    assert w.vertical_zero.value == v_zero
    assert w.magnetic_declination.value == m_decl
    assert w.coordinate_1_name.value == c1_name
    assert w.coordinate_1_value.value == c1_value
    assert w.coordinate_2_name.value == c2_name
    assert w.coordinate_2_value.value == c2_value


