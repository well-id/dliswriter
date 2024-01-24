import logging
import lasio  # type: ignore

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type


logger = logging.getLogger(__name__)


def make_dlis_file_spec_from_las(data_file_path: file_name_type) -> tuple[DLISFile, None]:
    data = lasio.read(data_file_path)

    df = DLISFile()
    df.add_origin("ORIGIN", file_set_number=1)

    channels = []
    for col_name in data.keys():
        channel_data = data[col_name]
        ch = df.add_channel(col_name, data=channel_data)
        channels.append(ch)

    df.add_frame('MAIN', channels=channels)

    return df, None
