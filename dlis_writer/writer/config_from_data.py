import h5py
from configparser import ConfigParser
from pathlib import Path
from argparse import ArgumentParser
from typing import Union
import logging

from dlis_writer.utils.loaders import load_config
from dlis_writer.utils.logging import install_logger


logger = logging.getLogger(__name__)


default_base_config_file_name = Path(__file__).resolve().parent / 'basic_config.ini'


def make_parser():
    parser = ArgumentParser("Creating config file from data")
    parser.add_argument('-df', '--data-file-name', required=True,
                        help="HDF5 data file to create the config for")
    parser.add_argument('-cf', '--config-file-name', required=True,
                        help="Output config file name")
    parser.add_argument('-bcf', '--base-config-file-name', default=default_base_config_file_name,
                        help="Config file to base the new config on")
    parser.add_argument('--time-based', action='store_true', default=False,
                        help="Make a time-based config file (default is depth-based)")

    return parser


def add_index_config(config: ConfigParser, time_based=False):
    if 'index_type' not in config['Frame'].keys():
        config['Frame']['index_type'] = 'TIME' if time_based else 'DEPTH'

    if 'spacing.units' not in config['Frame'].keys():
        config['Frame']['spacing.units'] = 's' if time_based else 'm'


def add_channel_config_from_data(data: h5py.File, config: ConfigParser):
    sections = []

    for dataset in yield_h5_datasets(data):
        dataset_name = dataset.name
        channel_name = dataset_name.split('/')[-1]
        section = f"Channel-{channel_name}"
        if section not in config.sections():
            config.add_section(section)
            config[section]['name'] = channel_name
            config[section]['dataset_name'] = dataset_name
        sections.append(section)

    if sections:
        config['Frame']['channels'] = ', '.join(sections)


def yield_h5_datasets(h5_object: Union[h5py.File, h5py.Group]):
    for key, value in h5_object.items():
        if isinstance(value, h5py.Dataset):
            yield value
        if isinstance(value, h5py.Group):
            yield from yield_h5_datasets(value)


def extend_config(data, config, time_based=False):
    add_index_config(config, time_based=time_based)
    add_channel_config_from_data(data, config)


def write_config(config: ConfigParser, file_name: str):
    if Path(file_name).exists():
        logger.warning(f"Overwriting existing config file at '{file_name}'")

    with open(file_name, 'w') as f:
        config.write(f)
    logger.info(f"Created new config file at '{file_name}'")


def make_config_from_data(data: h5py.File, base_config_file_name: str, output_config_file_name: str, **kwargs):
    logger.info(f"Loading base config from '{base_config_file_name}'")
    config: ConfigParser = load_config(base_config_file_name)

    extend_config(data, config, **kwargs)
    write_config(config, output_config_file_name)


def main():
    pargs = make_parser().parse_args()

    data = h5py.File(pargs.data_file_name, 'r')

    exception = None
    try:
        make_config_from_data(
            data,
            base_config_file_name=pargs.base_config_file_name,
            output_config_file_name=pargs.config_file_name,
            time_based=pargs.time_based
        )
    except Exception as exc:
        exception = exc
    finally:
        data.close()
    if exception:
        raise exception


if __name__ == '__main__':
    install_logger(logger)
    main()

