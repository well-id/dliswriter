import pytest

from dlis_writer.logical_record.eflr_types import Axis
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize(("idx", "name", "axis_id", "coordinates"), (
        (0, "Axis-1", "First axis", [40.395241, 27.792471]),
        (1, "Axis-X", "Axis not added to computation", [8])
))
def test_from_config(config_params, idx, name, axis_id, coordinates):
    axis = Axis.make_from_config(config_params, key=name)

    assert axis._name == name
    assert axis.axis_id.value == axis_id
    assert axis.coordinates.value == coordinates
