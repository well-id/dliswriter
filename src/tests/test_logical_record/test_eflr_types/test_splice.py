from dlis_writer.logical_record.eflr_types import SpliceSet, SpliceItem, ZoneItem, ChannelItem


def test_splice_creation(zone1: ZoneItem, zone3: ZoneItem, chan: ChannelItem, channel2: ChannelItem,
                         channel1: ChannelItem, channel3: ChannelItem) -> None:
    """Test creating SpliceItem."""

    splice = SpliceItem(
        "splc1",
        zones=(zone1, zone3),
        input_channels=(channel2, channel1, chan),
        output_channel=channel3
    )

    assert splice.name == "splc1"

    for i, n in enumerate(("Zone-1", "Zone-3")):
        assert splice.zones.value[i].name == n

    for i, n in enumerate(("Channel 2", "Channel 1", "some_channel")):
        assert splice.input_channels.value[i].name == n

    assert splice.output_channel.value.name == 'Channel 3'

    assert isinstance(splice.parent, SpliceSet)
    assert splice.parent.set_name is None
