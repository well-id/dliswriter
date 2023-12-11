from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.splice import SpliceTable, SpliceItem

from tests.common import base_data_path, config_params


def test_from_config(config_params: ConfigParser):
    """Test creating SpliceObject from config."""

    splice: SpliceItem = SpliceItem.from_config(config_params, key="Splice-1")

    assert splice.name == "splc1"

    for i, n in enumerate(("Zone-1", "Zone-2")):
        assert splice.zones.value[i].name == n

    for i, n in enumerate(("Channel 1", "Channel 2")):
        assert splice.input_channels.value[i].name == n

    assert splice.output_channel.value.name == 'amplitude'
