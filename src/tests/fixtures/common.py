from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel




def make_origin():
    origin = eflr_types.OriginItem(
        "DEFAULT ORIGIN",
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
    )

    return origin


def make_file_header():
    return eflr_types.FileHeaderItem("DEFAULT FHLR", sequence_number=1)


def make_sul():
    return StorageUnitLabel("DEFAULT STORAGE SET", sequence_number=1)


def make_dlis_file_base():
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    return df
