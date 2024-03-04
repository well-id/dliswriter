import logging
import pandas as pd
from typing import Optional

from dlis_writer.file import DLISFile
from dlis_writer.utils.types import file_name_type


logger = logging.getLogger(__name__)


def read_data(data_file_path: file_name_type) -> pd.DataFrame:
    """Read an input data file into a pandas DataFrame."""

    ext = str(data_file_path).split('.')[-1].lower()
    if ext == 'csv':
        data = pd.read_csv(data_file_path)
    elif ext in ('xls', 'xlsx'):
        data = pd.read_excel(data_file_path)
    else:
        raise ValueError(f"Expected a csv or xls(x) file; got {data_file_path}")

    return data


def make_dlis_file_spec_from_csv_or_xlsx(data_file_path: file_name_type, index_col_name: Optional[str] = None
                                         ) -> tuple[DLISFile, None]:
    """Create a DLISFile object according to the contents of the input data file."""

    data = read_data(data_file_path)

    df = DLISFile()
    df.add_origin("ORIGIN")

    channels = []

    def add_channel(col_name: str) -> None:
        ch = df.add_channel(col_name, data=data[col_name].to_numpy())
        channels.append(ch)

    if index_col_name is not None:
        add_channel(index_col_name)

    for cn in data.columns:
        if cn == index_col_name:
            continue
        add_channel(cn)

    df.add_frame('MAIN', channels=channels)

    return df, None
