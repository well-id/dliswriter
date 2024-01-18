from datetime import datetime, timedelta

from dlis_writer.logical_record.eflr_types.origin import OriginItem, OriginSet


def test_origin_creation() -> None:
    """Test creating OriginItem."""

    origin = OriginItem(
        'DEFAULT ORIGIN',
        creation_time="2050/03/02 15:30:00",
        file_id="WELL ID",
        file_set_name="Test file set name",
        file_set_number=1,
        file_number=8,
        run_number=13,
        well_id=5,
        well_name="Test well name",
        field_name="Test field name",
        company="Test company",
        parent=OriginSet()
    )

    assert origin.name == 'DEFAULT ORIGIN'

    assert origin.creation_time.value == datetime(year=2050, month=3, day=2, hour=15, minute=30)
    assert origin.file_id.value == "WELL ID"
    assert origin.file_set_name.value == "Test file set name"
    assert origin.file_set_number.value == 1
    assert origin.file_number.value == 8
    assert origin.run_number.value == 13
    assert origin.well_id.value == 5
    assert origin.well_name.value == "Test well name"
    assert origin.field_name.value == "Test field name"
    assert origin.company.value == "Test company"

    # not set - absent from config
    assert origin.producer_name.value is None
    assert origin.product.value is None
    assert origin.order_number.value is None
    assert origin.version.value is None
    assert origin.programs.value is None

    # OriginSet
    assert isinstance(origin.parent, OriginSet)
    assert origin.parent.set_name is None


def test_origin_creation_no_dtime_in_attributes() -> None:
    """Test that if creation_time is missing, the origin gets the current date and time as creation time."""

    origin = OriginItem("Some origin name", well_name="Some well name", file_set_number=11, parent=OriginSet())

    assert origin.name == "Some origin name"
    assert origin.well_name.value == "Some well name"

    assert timedelta(seconds=0) <= datetime.now() - origin.creation_time.value < timedelta(seconds=1)


def test_origin_creation_no_attributes() -> None:
    """Test creating OriginItem with minimum number of parameters."""

    origin = OriginItem("Some origin name", file_set_number=2, parent=OriginSet())

    assert origin.name == "Some origin name"
    assert origin.well_name.value is None

    assert timedelta(seconds=0) <= datetime.now() - origin.creation_time.value < timedelta(seconds=1)
