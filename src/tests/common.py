from dlis_writer.logical_record.eflr_types import eflr_sets


def clear_eflr_instance_registers():
    """Remove all defined instances of EFLR from the internal dicts. Clear the EFLRObject dicts of the instances."""

    for eflr_type in eflr_sets:
        for eflr in eflr_type.get_all_sets():
            eflr.clear_eflr_item_dict()
        eflr_type.clear_set_instance_dict()
