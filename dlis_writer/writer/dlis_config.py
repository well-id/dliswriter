import os
import h5py
from configparser import ConfigParser
from pathlib import Path
from argparse import ArgumentParser, Namespace
from typing import Union, Optional
from typing_extensions import Self
import logging
from pkg_resources import resource_filename

from dlis_writer.utils.logging import install_logger
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


default_base_config_file_name = Path(resource_filename('dlis_writer', 'resources/basic_config.ini'))
path_type = Union[str, bytes, os.PathLike]


def load_config(fname: path_type) -> ConfigParser:
    """Create a ConfigParser object and populate it with config information found in the provided file.

    Args:
        fname   :   Path to the file containing config info.

    Returns:
        A ConfigParser object with information contained in the file.
    """

    if not os.path.exists(fname):
        raise ValueError(f"Config file does not exist at {fname}")

    cfg = ConfigParser()
    cfg.read(fname)
    return cfg


class DLISConfig:
    """Create a config object for DLIS file specification. Add features to auto-generate missing config information."""

    def __init__(self, config: ConfigParser):
        """Initialise DLISConfig.

        Args:
            config  :   ConfigParser object containing (some of) the DLIS file specification.
        """

        self._config = config

    @property
    def config(self) -> ConfigParser:
        """Config object with DLIS specification."""

        return self._config

    @classmethod
    def from_config_file(cls, fname: path_type) -> Self:
        """Create a DLISConfig object by loading a config file.

        Args:
            fname   :   Name of the file to be loaded.

        Returns:
            A DLISConfig object set up with the information contained in the provided file.
        """

        return cls(load_config(fname))

    @classmethod
    def make_parser(cls) -> ArgumentParser:
        """Create an argument parser which can be used to create a DLISConfig object using 'from_parser_args' method."""

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
    def from_parser_args(cls, pargs: Namespace) -> Self:
        """Create a DLISConfig object using information from parsed arguments (from 'make_parser' method)."""

        return cls.from_h5_data_file(
            pargs.data_file_name,
            base_config_file_name=pargs.base_config_file_name,
            output_config_file_name=pargs.config_file_name,
            time_based=pargs.time_based
        )

    def add_index_config(self, time_based: bool = False):
        """Add frame index information ('index_type' and 'spacing.units') to the config object.

        Args:
            time_based  :   If True, the index_type is set to 'TIME' and the spacing units - to 's'.
                            Otherwise, the values are 'DEPTH' and 'm'.
        """

        if 'index_type' not in self._config['Frame'].keys():
            self._config['Frame']['index_type'] = 'TIME' if time_based else 'DEPTH'

        if 'spacing.units' not in self._config['Frame'].keys():
            self._config['Frame']['spacing.units'] = 's' if time_based else 'm'

    def add_channel_config_from_h5_data(self, data: h5py.File):
        """Add channels specifications to the config, taking all datasets found in the provided HDF5 file.

        Args:
            data    :   A h5py.File object to base the channel config on.
        """

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
        """Traverse a HDF5 (h5py) object in a recursive manner and yield all datasets it contains.

        Args:
            h5_object   : HDF5 File or Group to traverse.

        Yields:
            h5py Dataset objects contained in the provided File or Group.
        """

        for key, value in h5_object.items():
            if isinstance(value, h5py.Dataset):
                yield value
            if isinstance(value, h5py.Group):
                yield from DLISConfig.yield_h5_datasets(value)

    def write(self, file_name: path_type):
        """Store the config object in a file.

        Args:
            file_name   :   Name of the config file to be created.
        """

        if Path(file_name).exists():
            logger.warning(f"Overwriting existing config file at '{file_name}'")

        with open(file_name, 'w') as f:
            self._config.write(f)
        logger.info(f"Created new config file at '{file_name}'")

    @classmethod
    def from_h5_data(cls, data: h5py.File, base_config_file_name: Optional[path_type] = None,
                     output_config_file_name: Optional[path_type] = None, time_based: bool = False) -> Self:
        """Create a DLISConfig object by analysing the contents of the provided HDF5 data file.

        Args:
            data                    :   The data file to base the config on.
            base_config_file_name   :   Name of a config file which will serve as a base for the created config.
                                        This method adds information concerning the frame's index and the channels.
                                        Other information, such as file header and storage unit label specs
                                        (and possibly additional objects, such as parameters, paths, zones, etc.)
                                        cannot be inferred from the data and should come from the provided base config.
            output_config_file_name :   If provided, the created config will be saved to a file of this name.
            time_based              :   If True, specify the frame index as time-based. Otherwise, make it depth-based.

        Returns:
            A DLISConfig object set up with the information retrieved from the data file.
        """

        base_config_file_name = base_config_file_name or default_base_config_file_name
        logger.info(f"Loading base config from '{base_config_file_name}'")

        cfg = cls(load_config(base_config_file_name))
        cfg.add_index_config(time_based=time_based)
        cfg.add_channel_config_from_h5_data(data)

        if output_config_file_name:
            cfg.write(output_config_file_name)
        else:
            logger.debug("Output config file name not provided; config will not be stored to a file")

        return cfg

    @classmethod
    def from_h5_data_file(cls, data_file_name: path_type, **kwargs) -> Self:
        """Create a DLISConfig object by analysing the contents of the provided HDF5 data file (to be loaded here).

        Args:
            data_file_name  :   Name of the HDF5 file to be loaded.
            **kwargs        :   Keyword arguments passed to 'from_h5_data'. See the latter method's docstring for
                                specification of the accepted arguments.

        Returns:
            A DLISConfig object set up with the information retrieved from the data file.
        """

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

        return cfg  # no, it's not referenced before assignment


def main():
    """Create a DLIS specification config object and store it in a config file, according to the command line args."""

    install_logger(logger)
    pargs = DLISConfig.make_parser().parse_args()
    DLISConfig.from_parser_args(pargs)


if __name__ == '__main__':
    main()

