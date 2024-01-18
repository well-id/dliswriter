from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel


def make_origin() -> eflr_types.OriginItem:
    origin = eflr_types.OriginItem(
        "DEFINING ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_set_number=1,
        parent=eflr_types.OriginItem.make_parent()
    )

    return origin


def make_file_header() -> eflr_types.FileHeaderItem:
    return eflr_types.FileHeaderItem(
        "DEFAULT FHLR",
        sequence_number=1,
        parent=eflr_types.FileHeaderItem.make_parent()
    )


def make_sul() -> StorageUnitLabel:
    return StorageUnitLabel("DEFAULT STORAGE SET", sequence_number=1)
