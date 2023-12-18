from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel


def make_origin():
    origin = eflr_types.OriginItem(
        "DEFINING ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_set_number=1
    )

    return origin


def make_file_header():
    return eflr_types.FileHeaderItem("DEFAULT FHLR", sequence_number=1)


def make_sul():
    return StorageUnitLabel("DEFAULT STORAGE SET", sequence_number=1)
