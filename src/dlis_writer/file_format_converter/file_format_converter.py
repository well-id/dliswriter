import logging
from typing import Optional, Union

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type, data_form_type
from dlis_writer.file_format_converter.hdf5_converter import make_dlis_file_spec_from_hdf5
from dlis_writer.file_format_converter.csv_xlxs_converter import make_dlis_file_spec_from_csv_or_xlsx


logger = logging.getLogger(__name__)


def make_dlis_file_spec(data_file_path: file_name_type) -> tuple[DLISFile, Union[data_form_type, None]]:
    data_file_path = str(data_file_path)
    ext = data_file_path.split('.')[-1].lower()
    if ext in ('h5', 'hdf5'):
        df, data_source = make_dlis_file_spec_from_hdf5(data_file_path=data_file_path)
    elif ext in ('csv', 'xls', 'xlsx'):
        df, data_source = make_dlis_file_spec_from_csv_or_xlsx(data_file_path=data_file_path)
    else:
        raise ValueError(f"Could not determine converter from file extension '{ext}'")

    return df, data_source


def write_dlis_from_data_file(data_file_path: file_name_type, output_file_path: file_name_type,
                              input_chunk_size: Optional[int] = None, output_chunk_size: Optional[int] = None) -> None:

    dlis_file, data_source = make_dlis_file_spec(data_file_path)

    dlis_file.write(
        output_file_path,
        data=data_source,
        input_chunk_size=input_chunk_size,
        output_chunk_size=output_chunk_size,
    )
