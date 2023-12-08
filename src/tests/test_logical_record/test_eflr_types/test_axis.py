import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.axis import AxisTable, AxisItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("idx", "name", "axis_id", "coordinates"), (
        (0, "Axis-1", "First axis", [40.395241, 27.792471]),
        (1, "Axis-X", "Axis not added to computation", [8])
))
def test_from_config(config_params: ConfigParser, idx: int, name: str, axis_id: str, coordinates: list):
    """Check that an AxisObject is correctly set up from config info."""

    axis: AxisItem = AxisTable.make_eflr_item_from_config(config_params, key=name)

    assert axis.name == name
    assert axis.axis_id.value == axis_id
    assert axis.coordinates.value == coordinates
