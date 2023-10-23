import pytest

from dlis_writer.logical_record.eflr_types import Process
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize(("key", "name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        ("Process-1", "Process 1", ["radius"], ["amplitude", "Channel 2"], ["COMPT-1"], ["COMPT2"]),
        ("Process-2", "Prc2", ["Channel 1"], ["Channel 2"], ["COMPT2", "COMPT-1"], []),
))
def test_process_params(config_params, key, name, input_channels, output_channels, input_compts, output_compts):
    proc = Process.make_from_config(config_params, key=key)

    assert proc.name == name

    for i, n in enumerate(input_channels):
        assert proc.input_channels.value[i].name == n

    for i, n in enumerate(output_channels):
        assert proc.output_channels.value[i].name == n

    for i, n in enumerate(input_compts):
        assert proc.input_computations.value[i].name == n

    for i, n in enumerate(output_compts):
        assert proc.output_computations.value[i].name == n

