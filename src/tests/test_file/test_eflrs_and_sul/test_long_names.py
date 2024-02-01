from dlisio import dlis    # type: ignore  # untyped library


def test_long_name_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Test attributes of the LongName object in the DLIS file."""

    w = short_dlis.longnames[0]
    t = 'SOME ASCII TEXT'

    assert w.modifier == [t]
    assert w.quantity == t
    assert w.quantity_mod == [t]
    assert w.altered_form == t
    assert w.entity == t
    assert w.entity_mod == [t]
    assert w.entity_nr == t
    assert w.entity_part == t
    assert w.entity_part_nr == t
    assert w.generic_source == t
    assert w.source_part == [t]
    assert w.source_part_nr == [t]
    assert w.conditions == [t]
    assert w.standard_symbol == t
    assert w.private_symbol == t
    assert w.origin == 42
