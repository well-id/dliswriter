from dlisio import dlis    # type: ignore  # untyped library

from tests.common import check_list_of_objects


def test_splices(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Splice objects in the DLIS file matches the expected one."""

    splices = short_dlis.splices
    assert len(splices) == 1


def test_splice_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Test attributes of the Splice object in the new DLIS file."""

    splice = short_dlis.splices[0]

    assert splice.name == "splc1"
    assert splice.origin == 42

    check_list_of_objects(splice.zones, ("Zone-1", "Zone-2"))
    check_list_of_objects(splice.input_channels, ("Channel 1", "Channel 2"))

    assert splice.output_channel.name == 'amplitude'
