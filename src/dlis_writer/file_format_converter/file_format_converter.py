import logging
from typing import Optional, Union

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type, data_form_type
from dlis_writer.file_format_converter.hdf5_converter import make_dlis_file_spec_from_hdf5
from dlis_writer.file_format_converter.csv_xlxs_converter import make_dlis_file_spec_from_csv_or_xlsx
from dlis_writer.file_format_converter.las_converter import make_dlis_file_spec_from_las


logger = logging.getLogger(__name__)


def make_dlis_file_spec(data_file_path: file_name_type) -> tuple[DLISFile, Union[data_form_type, None]]:
    """Create a DLISFile object, containing basic objects and data reference.

    The configured DLISFile object contains:
        - the required Storage Unit Label and File Header objects
        - an Origin
        - as many Channels as there were data sets found in the source data file,
        - a Frame containing all the Channels.

    Args:
        data_file_path  :   Path to the input data file.

    Returns:
        - df: Configured DLIS file object,
        - data_source: data source to be passed to df.write(). This is the file name for HDF5 files and None otherwise
            (for csv, xls(x), and las files, the data are passed to the channel objects; For HDF5 this is not done
            to avoid copying possibly large datasets).
    """

    data_file_path = str(data_file_path)
    ext = data_file_path.split('.')[-1].lower()
    if ext in ('h5', 'hdf5'):
        df, data_source = make_dlis_file_spec_from_hdf5(data_file_path=data_file_path)
    elif ext in ('csv', 'xls', 'xlsx'):
        df, data_source = make_dlis_file_spec_from_csv_or_xlsx(data_file_path=data_file_path)
    elif ext == 'las':
        df, data_source = make_dlis_file_spec_from_las(data_file_path=data_file_path)
    else:
        raise ValueError(f"Could not determine converter from file extension '{ext}' ({data_file_path})")

    return df, data_source


def write_dlis_from_data_file(data_file_path: file_name_type, output_file_path: file_name_type,
                              input_chunk_size: Optional[int] = None, output_chunk_size: Optional[int] = None) -> None:
    """Create a DLIS file based on an input data file.

    Args:
        data_file_path      :   Path to the input data file.
        output_file_path    :   Path to the output DLIS file.
        input_chunk_size    :   Number of rows of the input data to be loaded and processed at a time.
        output_chunk_size   :   Size (in bytes) of output DLIS file chunks written to the file at a time.
    """

    dlis_file, data_source = make_dlis_file_spec(data_file_path)

    dlis_file.write(
        output_file_path,
        data=data_source,
        input_chunk_size=input_chunk_size,
        output_chunk_size=output_chunk_size,
    )
