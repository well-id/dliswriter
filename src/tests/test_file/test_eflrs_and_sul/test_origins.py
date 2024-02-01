from datetime import datetime
from dlisio import dlis    # type: ignore  # untyped library
from pytz import utc


def test_origin(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Origin in the new DLIS file."""

    assert len(short_dlis.origins) == 1

    origin = short_dlis.origins[0]

    assert origin.name == "DEFAULT ORIGIN"

    # dlisio doesn't add time zone info to the parsed datetime objects, so we use utc.localize here to put it in UTC
    assert (utc.localize(origin.creation_time) ==
            datetime.strptime("2050/03/02 15:30:00", "%Y/%m/%d %H:%M:%S").astimezone(utc))

    assert origin.file_id == short_dlis.fileheader.id
    assert origin.file_set_name == "Test file set name"
    assert origin.file_set_nr == 42
    assert origin.origin == 42
    assert origin.file_nr == 8
    assert origin.run_nr == [13]
    assert origin.well_id == 5
    assert origin.well_name == "Test well name"
    assert origin.field_name == "Test field name"
    assert origin.company == "Test company"

    # not set - absent from config
    assert origin.producer_name is None
    assert origin.product is None
    assert origin.order_nr is None
    assert origin.version is None
    assert origin.programs == []
