import numpy as np
import logging

from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record.eflr_types import Origin
from dlis_writer.utils.logging import install_logger


# colored logs output
logger = logging.getLogger(__name__)
install_logger(logger)


# set up origin & file header with custom parameters - by creating an instance or dict of kwargs
origin = Origin.make_object("DEFAULT ORIGIN", file_set_number=1, company="XXX")
file_header = {'sequence_number': 2}


# create DLISFile instance, pass the origin and file header
df = DLISFile(origin=origin, file_header=file_header)


# change parameters of already added objects
df.origin.order_number.value = "352"


# define axes - metadata objects for channels
ax1 = df.add_axis('AXIS1', coordinates=["40 23' 42.8676'' N", "27 47' 32.8956'' E"], axis_id='AXIS 1')
ax1.spacing.value = 0.2
ax1.spacing.units = 'm'
ax2 = df.add_axis('AXIS2', spacing=5, coordinates=[1, 2, 3.5])


# define frame 1: depth-based with 3 channels, 100 rows each
n_rows_depth = 100
ch1 = df.add_channel('DEPTH', data=np.arange(n_rows_depth) / 10, units='m')     # index channel - always scalar
ch2 = df.add_channel("RPM", data=(np.arange(n_rows_depth) % 10).astype(float), axis=ax1)  # 1D data
ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows_depth, 5))    # image channel - 2D data
main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')


# define frame 2: time-based with 2 channels, 200 rows each
n_rows_time = 200
ch4 = df.add_channel('TIME', data=np.arange(n_rows_time) / 4, units='s', axis=ax2)  # index channel for frame 2
ch5 = df.add_channel('TEMPERATURE', data=20+5*np.random.rand(n_rows_time), units='degC')
second_frame = df.add_frame('TIME FRAME', channels=(ch4, ch5), index_type='NONSTANDARD')


# write the file
df.write('./tmp.DLIS', input_chunk_size=20)
