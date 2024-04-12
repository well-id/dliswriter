"""This is an example of how to create a DLIS file with multiple frames with equivalent channels - i.e. the same channel
names used in different frames (but referring to separate datasets).

The procedure is the same as for standard DLIS files.
When inspecting the objects, one might notice that:
    - copy_number of the channels is different - 0 for channels of frame 1, 1 for channels of frame 2
    - dataset_name attributes of the corresponding channels are also different, so that datasets are not overwritten.
"""

import numpy as np
import logging

from dliswriter import DLISFile, EFLRItem, enums, eflr_types
from dliswriter.utils.logging import install_colored_logger


# colored logs output
install_colored_logger(logging.getLogger('dliswriter'))


# create DLISFile instance; optionally, pass arguments for creating file header & storage unit label
df = DLISFile(
    sul_sequence_number=2,
    fh_sequence_number=2,
    fh_id="MAIN FILE",
    fh_identifier="X"
)

# add origin - required item
df.add_origin(
    "DEFAULT ORIGIN",
    file_set_number=80,
    company="XXX"
)


# define frame 1
n_rows_1 = 100
ch_depth_1 = df.add_channel(
    'DEPTH',
    data=np.arange(n_rows_1),
    units=enums.Unit.METER
)
ch_rpm_1 = df.add_channel(
    "RPM",
    data=10 * np.random.rand(n_rows_1)
)
ch_amp_1 = df.add_channel(
    "AMPLITUDE",
    data=np.random.rand(n_rows_1, 10)
)
frame1 = df.add_frame(
    "FRAME1",
    channels=(ch_depth_1, ch_rpm_1, ch_amp_1),
    index_type=enums.FrameIndexType.BOREHOLE_DEPTH
)


# define frame 2
n_rows_2 = 200
ch_depth_2 = df.add_channel(
    'DEPTH',
    data=np.arange(n_rows_2),
    units=enums.Unit.METER
)
ch_rpm_2 = df.add_channel(
    "RPM",
    data=(np.arange(n_rows_2) % 10).astype(np.int32)
)
ch_amp_2 = df.add_channel(
    "AMPLITUDE",
    data=np.arange(n_rows_2 * 5).reshape(n_rows_2, 5) % 6
)
frame2 = df.add_frame(
    "FRAME2",
    channels=(ch_depth_2, ch_rpm_2, ch_amp_2),
    index_type=enums.FrameIndexType.BOREHOLE_DEPTH
)


# write the file
df.write('./tmp.DLIS')


# print the copy_number and dataset_name info of the objects for inspection
def describe_item(o: EFLRItem) -> None:
    s = f"{o}: \n\tcopy_number = {o.copy_number}"

    if isinstance(o, eflr_types.ChannelItem):
        s += f"\n\tdataset_name = {o.dataset_name}"

    print(s)


for eflr_item in (frame1, ch_depth_1, ch_rpm_1, ch_amp_1, frame2, ch_depth_2, ch_rpm_2, ch_amp_2):
    describe_item(eflr_item)
