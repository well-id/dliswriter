from datetime import datetime, timedelta
import numpy as np
import pytest

from dliswriter.logical_record.eflr_types.origin import OriginItem, OriginSet
from dliswriter.utils.internal.struct_writer import ULONG_OFFSET
from dliswriter import high_compatibility_mode_decorator


def test_origin_creation() -> None:
    """Test creating OriginItem."""

    origin = OriginItem(
        "DEFAULT ORIGIN",
        parent=OriginSet(),
        origin_reference=1,
        file_set_number=1,
        creation_time="2050/03/02 15:30:00",
        file_id="WELL ID",
        file_set_name="Test file set name",
        file_number=8,
        run_number=13,
        well_id="5",
        well_name="Test well name",
        field_name="Test field name",
        company="Test company",
    )

    assert origin.name == "DEFAULT ORIGIN"

    assert origin.creation_time.value == datetime(
        year=2050, month=3, day=2, hour=15, minute=30
    )
    assert origin.file_id.value == "WELL ID"
    assert origin.file_set_name.value == "Test file set name"
    assert origin.file_set_number.value == 1
    assert origin.origin_reference == 1
    assert origin.run_number.value == 13
    assert origin.well_id.value == "5"
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

    origin = OriginItem(
        "Some origin name",
        well_name="Some well name",
        origin_reference=11,
        parent=OriginSet(),
    )

    assert origin.name == "Some origin name"
    assert origin.well_name.value == "Some well name"

    assert (
        timedelta(seconds=0)
        <= datetime.now() - origin.creation_time.value
        < timedelta(seconds=1)
    )


def test_origin_creation_no_attributes() -> None:
    """Test creating OriginItem with minimum number of parameters."""

    origin = OriginItem("Some origin name", origin_reference=1, parent=OriginSet())

    assert origin.name == "Some origin name"
    assert origin.well_name.value is None

    assert origin.file_set_number.value is not None
    assert isinstance(origin.file_set_number.value, int)
    assert 1 <= origin.file_set_number.value <= np.iinfo(np.uint32).max - ULONG_OFFSET

    assert (
        timedelta(seconds=0)
        <= datetime.now() - origin.creation_time.value
        < timedelta(seconds=1)
    )

    origin.make_item_body_bytes()  # this is where defaults are set
    assert origin.field_name.value == "WILDCAT"  # default according to RP66


def test_no_reassign_file_set_number() -> None:
    origin = OriginItem("Some origin name", origin_reference=1, parent=OriginSet())

    with pytest.raises(
        RuntimeError, match="File set number should not be reassigned.*"
    ):
        origin.file_set_number.value = 15


@high_compatibility_mode_decorator
def test_file_set_number_high_compat_mode() -> None:
    parent = OriginSet()

    origin1 = OriginItem("ORIGIN", origin_reference=1, parent=parent)
    assert origin1.file_set_number.value == 1

    origin2 = OriginItem(
        "ANOTHER-ORIGIN", origin_reference=2, parent=parent, file_set_number=15
    )
    assert origin2.file_set_number.value == 15

    origin3 = OriginItem("ORIG", origin_reference=3, parent=parent)
    assert origin3.file_set_number.value == 3


@pytest.mark.parametrize("name", ("MY-ORIGIN", "ORI_124", "421ORIGIN5"))
@high_compatibility_mode_decorator
def test_name_compatible(name: str) -> None:
    OriginItem(
        name, origin_reference=1, parent=OriginSet()
    )  # no error = name accepted, test passed


@pytest.mark.parametrize("name", ("Origin", "MY ORIGIN", "ORIGIN.3"))
@high_compatibility_mode_decorator
def test_name_not_compatible(name: str) -> None:
    with pytest.raises(
        ValueError,
        match=".*strings can contain only uppercase characters, digits, dashes, .*",
    ):
        OriginItem(name, origin_reference=1, parent=OriginSet())
