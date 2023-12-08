import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.process import ProcessTable, ProcessItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("key", "name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        ("Process-1", "Process 1", ["radius"], ["amplitude", "Channel 2"], ["COMPT-1"], ["COMPT2"]),
        ("Process-2", "Prc2", ["Channel 1"], ["Channel 2"], ["COMPT2", "COMPT-1"], []),
))
def test_process_params(config_params: ConfigParser, key: str, name: str, input_channels: list[str],
                        output_channels: list[str], input_compts: list[str], output_compts: list[str]):
    """Test creating ProcessObject from config."""

    proc: ProcessItem = ProcessItem.from_config(config_params, key=key)

    assert proc.name == name

    for i, n in enumerate(input_channels):
        assert proc.input_channels.value[i].name == n

    for i, n in enumerate(output_channels):
        assert proc.output_channels.value[i].name == n

    for i, n in enumerate(input_compts):
        assert proc.input_computations.value[i].name == n

    for i, n in enumerate(output_compts):
        assert proc.output_computations.value[i].name == n

