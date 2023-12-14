import pytest

from dlis_writer.logical_record.eflr_types.process import ProcessSet, ProcessItem


@pytest.mark.parametrize(("name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        ("Process 1", ["chan"], ["channel1", "channel3"], ["computation1"], ["computation2"]),
        ("Prc2", ["channel1"], ["channel2"], ["computation1", "computation2"], []),
))
def test_process_params(name: str, input_channels: list[str], output_channels: list[str], input_compts: list[str],
                        output_compts: list[str], request):
    """Test creating ProcessObject from config."""

    proc = ProcessItem(
        name,
        input_channels=[request.getfixturevalue(v) for v in input_channels],
        output_channels=[request.getfixturevalue(v) for v in output_channels],
        input_computations=[request.getfixturevalue(v) for v in input_compts],
        output_computations=[request.getfixturevalue(v) for v in output_compts]
    )

    assert proc.name == name

    for i, n in enumerate(input_channels):
        assert proc.input_channels.value[i] is request.getfixturevalue(input_channels[i])

    for i, n in enumerate(output_channels):
        assert proc.output_channels.value[i] is request.getfixturevalue(output_channels[i])

    for i, n in enumerate(input_compts):
        assert proc.input_computations.value[i] is request.getfixturevalue(input_compts[i])

    for i, n in enumerate(output_compts):
        assert proc.output_computations.value[i] is request.getfixturevalue(output_compts[i])

    assert isinstance(proc.parent, ProcessSet)
    assert proc.parent.set_name is None
