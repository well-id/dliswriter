import logging
import lasio  # type: ignore

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type


logger = logging.getLogger(__name__)


def make_dlis_file_spec_from_las(data_file_path: file_name_type) -> tuple[DLISFile, None]:
    """Create a DLISFile object according to the contents of the input data file."""

    data = lasio.read(data_file_path)

    df = DLISFile()
    df.add_origin("ORIGIN")

    channels = []
    for curve in data.curves:
        ch = df.add_channel(curve.mnemonic, data=curve.data, units=curve.unit, long_name=curve.descr)
        channels.append(ch)

    df.add_frame('MAIN', channels=channels)

    return df, None
