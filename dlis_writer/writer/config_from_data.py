import os

import h5py
from configparser import ConfigParser
from pathlib import Path
from argparse import ArgumentParser
from typing import Union
import logging

from dlis_writer.utils.loaders import load_config
from dlis_writer.utils.logging import install_logger
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


default_base_config_file_name = Path(__file__).resolve().parent / 'basic_config.ini'
path_type = Union[str, bytes, os.PathLike]


class DLISConfig:
    def __init__(self, config: ConfigParser):
        self._config = config

    @property
    def config(self):
        return self._config

    @classmethod
    def from_config_file(cls, fname):
        return cls(load_config(fname))

    @classmethod
    def make_parser(cls):
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

    @classmethod
    def from_parser_args(cls, pargs):
        return cls.from_h5_data_file(
            pargs.data_file_name,
            base_config_file_name=pargs.base_config_file_name,
            output_config_file_name=pargs.config_file_name,
            time_based=pargs.time_based
        )

    def add_index_config(self, time_based: bool = False):
        if 'index_type' not in self._config['Frame'].keys():
            self._config['Frame']['index_type'] = 'TIME' if time_based else 'DEPTH'

        if 'spacing.units' not in self._config['Frame'].keys():
            self._config['Frame']['spacing.units'] = 's' if time_based else 'm'

    def add_channel_config_from_data(self, data: h5py.File):
        sections = []

        for dataset in self.yield_h5_datasets(data):
            dataset_name = dataset.name
            channel_name = dataset_name.split('/')[-1]
            section = f"Channel-{channel_name}"
            if section not in self._config.sections():
                self._config.add_section(section)
                self._config[section]['name'] = channel_name
                self._config[section]['dataset_name'] = dataset_name
                self._config[section]['representation_code'] = (
                    str(ReprCodeConverter.determine_repr_code_from_numpy_dtype(dataset.dtype).value))
            sections.append(section)

        if sections:
            self._config['Frame']['channels'] = ', '.join(sections)

    @staticmethod
    def yield_h5_datasets(h5_object: Union[h5py.File, h5py.Group]):
        for key, value in h5_object.items():
            if isinstance(value, h5py.Dataset):
                yield value
            if isinstance(value, h5py.Group):
                yield from DLISConfig.yield_h5_datasets(value)

    def extend_from_h5_data(self, data: h5py.File, time_based: bool = False):
        self.add_index_config(time_based=time_based)
        self.add_channel_config_from_data(data)

    def write(self, file_name: path_type):
        if Path(file_name).exists():
            logger.warning(f"Overwriting existing config file at '{file_name}'")

        with open(file_name, 'w') as f:
            self._config.write(f)
        logger.info(f"Created new config file at '{file_name}'")

    @classmethod
    def from_h5_data(cls, data: h5py.File, base_config_file_name: path_type = None,
                     output_config_file_name: path_type = None, time_based: bool = False):
        base_config_file_name = base_config_file_name or default_base_config_file_name
        logger.info(f"Loading base config from '{base_config_file_name}'")

        cfg = cls(load_config(base_config_file_name))
        cfg.add_index_config(time_based=time_based)
        cfg.add_channel_config_from_data(data)

        if output_config_file_name:
            cfg.write(output_config_file_name)
        else:
            logger.debug("Output config file name not provided; config will not be stored to a file")

        return cfg

    @classmethod
    def from_h5_data_file(cls, data_file_name: path_type, **kwargs):
        data = h5py.File(data_file_name, 'r')

        exception = None
        try:
            cfg = cls.from_h5_data(data, **kwargs)
        except Exception as exc:
            exception = exc
        finally:
            data.close()
        if exception:
            raise exception

        return cfg


def main():
    pargs = DLISConfig.make_parser().parse_args()
    DLISConfig.from_parser_args(pargs)


if __name__ == '__main__':
    install_logger(logger)
    main()

