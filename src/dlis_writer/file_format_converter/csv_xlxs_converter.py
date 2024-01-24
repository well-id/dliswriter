import logging
import pandas as pd

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type


logger = logging.getLogger(__name__)


def read_data(data_file_path: file_name_type) -> pd.DataFrame:
    ext = str(data_file_path).split('.')[-1].lower()
    if ext == 'csv':
        data = pd.read_csv(data_file_path)
    elif ext in ('xls', 'xlsx'):
        data = pd.read_excel(data_file_path)
    else:
        raise ValueError(f"Expected a csv or xls(x) file; got {data_file_path}")

    return data


def make_dlis_file_spec_from_csv_or_xlsx(data_file_path: file_name_type) -> tuple[DLISFile, None]:
    data = read_data(data_file_path)

    df = DLISFile()
    df.add_origin("ORIGIN", file_set_number=1)

    channels = []
    for col_name in data.columns:
        ch = df.add_channel(col_name, data=data[col_name].to_numpy())
        channels.append(ch)

    df.add_frame('MAIN', channels=channels)

    return df, None
