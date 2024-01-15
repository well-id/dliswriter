import numpy as np
import logging

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.eflr_types.origin import OriginItem
from dlis_writer.utils.logging import install_logger


# colored logs output
logger = logging.getLogger(__name__)
install_logger(logger)


# set up origin & file header with custom parameters - by creating an instance or dict of kwargs
origin = OriginItem("DEFAULT ORIGIN", file_set_number=1, company="XXX")
file_header = {'sequence_number': 2}


# create DLISFile instance, pass the origin and file header
df = DLISFile(origin=origin, file_header=file_header)


# define frame 1
n_rows_1 = 100
ch_depth_1 = df.add_channel('DEPTH', data=np.arange(n_rows_1), units='m')
ch_rpm_1 = df.add_channel("RPM", data=10 * np.random.rand(n_rows_1))
ch_amp_1 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows_1, 10))
frame1 = df.add_frame("FRAME1", channels=(ch_depth_1, ch_rpm_1, ch_amp_1), index_type='BOREHOLE-DEPTH')


for ch in (ch_depth_1, ch_rpm_1, ch_amp_1):
    ch.copy_number = 1


# define frame 2
n_rows_2 = 200
ch_depth_2 = df.add_channel('DEPTH', data=np.arange(n_rows_2), units='m')
ch_rpm_2 = df.add_channel("RPM", data=(np.arange(n_rows_2) % 10).astype(np.int32))
ch_amp_2 = df.add_channel("AMPLITUDE", data=np.arange(n_rows_2 * 5).reshape(n_rows_2, 5) % 6)
frame2 = df.add_frame("FRAME2", channels=(ch_depth_2, ch_rpm_2, ch_amp_2), index_type='BOREHOLE-DEPTH')

for ch in (ch_depth_2, ch_rpm_2, ch_amp_2):
    ch.copy_number = 2


# write the file
df.write('./tmp.DLIS')
