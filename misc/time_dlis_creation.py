from timeit import timeit
from datetime import timedelta
from time import sleep
from pathlib import Path
import os
from argparse import ArgumentParser
import logging

from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data
from dlis_writer.writer.mwe_dlis_creation import write_dlis_file, load_hdf5


parser = ArgumentParser("Timing DLIS writer execution")
pgroup = parser.add_mutually_exclusive_group()
pgroup.add_argument('-n', '--n-points', help='Number of data points', type=float, default=50e3)
pgroup.add_argument('-ifn', '--input-file-name', help='HDF5 data file to create the DLIS from')

parser.add_argument('--add-2d', action='store_true', default=False, help='Add 2D data entry')
parser.add_argument('-ne', '--n-execs', type=int, default=1,
                    help='Number of times the writer will be executed (for computing better statistics)')
parser.add_argument('--keep-output', action='store_true', default=False,
                    help='Do not remove the output DLIS file (created in the current working directory).')
parser.add_argument('--hide-logs', action='store_true', default=False,
                    help="Hide the logs coming from DLIS writer")
parser_args = parser.parse_args()


if parser_args.hide_logs:
    logging.getLogger('logical_record').setLevel(logging.WARNING)


if (ifn := parser_args.input_file_name) is None:
    n_samples = int(parser_args.n_points)
    data = create_data(n_samples, add_2d=parser_args.add_2d)
else:
    data = load_hdf5(parser_args.input_file_name)
    n_samples = data.shape[0]

n_execs = parser_args.n_execs
print(f"Timing DLIS writer ({n_execs} times) for {n_samples} samples...")
fname = Path(os.getcwd())/'timing_output.DLIS'


def func():
    write_dlis_file(data, dlis_file_name=fname)
    if not parser_args.keep_output:
        os.remove(fname)


exec_time = timeit(func, number=n_execs) / n_execs

sleep(0.1)  # let the logs be displayed before printing the timing summary
print(f"Mean DLIS writer execution time for {n_samples} samples is {timedelta(seconds=exec_time)}")
