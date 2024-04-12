import logging
import lasio  # type: ignore
from typing import Optional

from dliswriter.file import DLISFile
from dliswriter.utils.types import file_name_type


logger = logging.getLogger(__name__)


def make_dlis_file_spec_from_las(data_file_path: file_name_type, index_col_name: Optional[str] = None
                                 ) -> tuple[DLISFile, None]:
    """Create a DLISFile object according to the contents of the input data file."""

    if index_col_name is not None:
        raise NotImplementedError("Creating DLISFile from LAS data with index col name specified is not yet supported")

    data = lasio.read(data_file_path)

    df = DLISFile()
    df.add_origin("ORIGIN")

    channels = []
    for curve in data.curves:
        ch = df.add_channel(curve.mnemonic, data=curve.data, units=curve.unit, long_name=curve.descr)
        channels.append(ch)

    df.add_frame('MAIN', channels=channels)

    return df, None
