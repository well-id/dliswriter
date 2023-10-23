from dlis_writer.logical_record.eflr_types import Splice
from dlis_writer.tests.common import base_data_path, config_params


def test_from_config(config_params):
    splice = Splice.make_from_config(config_params, key="Splice-1")

    assert splice._name == "splc1"

    for i, n in enumerate(("Zone-1", "Zone-2")):
        assert splice.zones.value[i]._name == n

    for i, n in enumerate(("Channel 1", "Channel 2")):
        assert splice.input_channels.value[i]._name == n

    assert splice.output_channel.value._name == 'amplitude'
