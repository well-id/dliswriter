from dlis_writer.logical_record.eflr_types.long_name import LongNameSet, LongNameItem


def test_from_config() -> None:
    """Test creating LongNameObject."""

    t = 'SOME ASCII TEXT'

    w = LongNameItem(
        "some long name",
        general_modifier=[t],
        quantity=t,
        quantity_modifier=[t],
        altered_form=t,
        entity=t,
        entity_modifier=[t],
        entity_number=t,
        entity_part=t,
        entity_part_number=t,
        generic_source=t,
        source_part=[t],
        source_part_number=[t],
        conditions=[t],
        standard_symbol=t,
        private_symbol=t,
        parent=LongNameSet()
    )

    assert w.general_modifier.value == [t]
    assert w.quantity.value == t
    assert w.quantity_modifier.value == [t]
    assert w.altered_form.value == t
    assert w.entity.value == t
    assert w.entity_modifier.value == [t]
    assert w.entity_number.value == t
    assert w.entity_part.value == t
    assert w.entity_part_number.value == t
    assert w.generic_source.value == t
    assert w.source_part.value == [t]
    assert w.source_part_number.value == [t]
    assert w.conditions.value == [t]
    assert w.standard_symbol.value == t
    assert w.private_symbol.value == t

    assert isinstance(w.parent, LongNameSet)
    assert w.parent.set_name is None
