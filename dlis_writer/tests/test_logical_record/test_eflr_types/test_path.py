import pytest

from dlis_writer.logical_record.eflr_types import Path, WellReferencePoint, Frame, Channel
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.mark.parametrize(("key", "name", "channels", "depth", "radial_drift", "angular_drift", "time"), (
        ("1", "PATH1", ("Channel 1", "Channel 2"), -187, 105, 64.23, 180),
        ("2", "path2", ("amplitude",), 120, 3, -12.3, 4)
))
def test_from_config(config_params, key, name, channels, depth, radial_drift, angular_drift, time):
    key = f"Path-{key}"
    p = Path.make_from_config(config_params, key=key)

    assert p._name == name
    assert isinstance(p.frame_type.value, Frame)
    assert p.frame_type.value._name == 'MAIN FRAME'
    assert isinstance(p.well_reference_point.value, WellReferencePoint)
    assert p.well_reference_point.value._name == 'AQLN WELL-REF'

    assert len(p.value.value) == len(channels)
    for i, c in enumerate(channels):
        assert isinstance(p.value.value[i], Channel)
        assert p.value.value[i]._name == c

    assert p.vertical_depth.value == depth
    assert p.radial_drift.value == radial_drift
    assert p.angular_drift.value == angular_drift
    assert p.time.value == time
