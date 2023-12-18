import pytest

from dlis_writer.logical_record.eflr_types.no_format import NoFormatSet, NoFormatItem


@pytest.mark.parametrize(("name", "consumer_name", "description"), (
        ("no_format_1", "SOME TEXT NOT FORMATTED", "TESTING-NO-FORMAT"),
        ("no_fmt2", "xyz", "TESTING NO FORMAT 2")
))
def test_creation(name: str, consumer_name: str, description: str):
    """Test creating NoFormatObject."""

    w = NoFormatItem(
        name=name,
        consumer_name=consumer_name,
        description=description
    )

    assert w.name == name
    assert w.consumer_name.value == consumer_name
    assert w.description.value == description

    assert isinstance(w.parent, NoFormatSet)
    assert w.parent.set_name is None
