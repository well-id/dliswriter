from dlisio import dlis    # type: ignore  # untyped library


from tests.common import N_COLS, select_channel, check_list_of_objects


def test_channel_properties(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of channels in the new DLIS file."""

    for name in ('posix time', 'surface rpm'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [1]
        assert chan.dimension == [1]
        assert chan.origin == 42

    for name in ('amplitude', 'radius', 'radius_pooh'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [N_COLS]
        assert chan.dimension == [N_COLS]
        assert chan.origin == 42

    assert short_dlis.object("CHANNEL", 'amplitude').units is None
    assert short_dlis.object("CHANNEL", 'radius').units == "in"
    assert short_dlis.object("CHANNEL", 'radius_pooh').units == "m"


def test_channel_long_name(short_dlis: dlis.file.LogicalFile) -> None:
    """Check long name channels in the new DLIS file."""

    ln = short_dlis.longnames[0]

    for name in ('Channel 2', 'surface rpm'):
        chan = select_channel(short_dlis, name)
        assert chan.long_name is ln

    chan = select_channel(short_dlis, "Some Channel")
    assert chan.long_name == "Some not so very long channel name"

    chan = select_channel(short_dlis, "channel_x")
    assert chan.long_name == "Channel not added to the frame"


def test_channel_not_in_frame(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that channel which was not added to frame is still in the file."""

    name = 'channel_x'
    select_channel(short_dlis, name)  # if no error - channel is found in the file
    assert not any(c.name == name for c in short_dlis.frames[0].channels)

