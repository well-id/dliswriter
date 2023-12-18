import os
import h5py    # type: ignore  # untyped library
import pytest
from copy import deepcopy
from pathlib import Path
from configparser import ConfigParser

from dlis_writer.writer.dlis_config import load_config
from dlis_writer.writer.dlis_file_comparator import compare
from dlis_writer.utils.source_data_wrappers import HDF5DataWrapper

from tests.common import N_COLS, load_dlis, select_channel, write_file
from tests.fixtures.time_based_dlis import write_time_based_dlis
from tests.fixtures.depth_based_dlis import write_depth_based_dlis


@pytest.fixture(scope='session')
def config_time_based(base_data_path: Path) -> ConfigParser:
    """Config object for a time-based DLIS file."""

    return load_config(base_data_path/'resources/mock_config_time_based.ini')


@pytest.fixture(scope='session')
def config_array_time_based(config_time_based: ConfigParser) -> ConfigParser:
    """Config object for a time-based file with Channel dataset names added."""

    c = deepcopy(config_time_based)
    for s in c.sections():
        if s.startswith('Channel'):
            if 'dataset_name' in c[s].keys():
                c[s]['dataset_name'] = c[s]['name']

    return c


@pytest.fixture
def new_dlis_path(base_data_path: Path):
    """Path for a new DLIS file to be created. The file is removed afterwards."""

    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


def test_correct_contents_rpm_only_depth_based(reference_data_path: Path, base_data_path: Path, new_dlis_path: Path):
    """Create a depth-based DLIS file with RPM data and compare it at binary level to the relevant reference DLIS."""

    write_depth_based_dlis(new_dlis_path, data=reference_data_path)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_rpm_depth_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_correct_contents_rpm_and_images_time_based(reference_data_path: Path, base_data_path: Path,
                                                    new_dlis_path: Path, config_time_based: ConfigParser):
    """Create a time-based DLIS file with RPM & images and compare it at binary level to the relevant reference DLIS."""

    write_file(data=reference_data_path, dlis_file_name=new_dlis_path, config=config_time_based)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_full_time_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_dlis_depth_based(short_reference_data: h5py.File, short_reference_data_path: Path, new_dlis_path: Path):
    """Create a depth-based DLIS file and check its basic parameters."""

    write_depth_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'depth'
        assert chan.units == 'm'
        assert chan.reprc == 7

        frame = f.frames[0]
        assert frame.index_type == 'DEPTH'

        index = short_reference_data['/contents/depth'][:]
        assert frame.index_min == index.min()
        assert frame.index_max == index.max()


def test_dlis_time_based(short_reference_data: h5py.File, short_reference_data_path: Path, new_dlis_path: Path):
    """Create a time-based DLIS file and check its basic parameters."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'posix time'
        assert chan.units == 's'
        assert chan.reprc == 7

        frame = f.frames[0]
        assert frame.index_type == 'TIME'
        index = short_reference_data['/contents/time'][:]
        assert frame.index_min == index.min()
        assert frame.index_max == index.max()


def test_repr_code(short_reference_data_path: Path, new_dlis_path: Path):
    """Test that representation codes for the channels in DLIS are stored correctly."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        assert select_channel(f, 'posix time').reprc == 7
        assert select_channel(f, 'surface rpm').reprc == 7
        assert select_channel(f, 'amplitude').reprc == 2
        assert select_channel(f, 'radius').reprc == 2
        assert select_channel(f, 'radius_pooh').reprc == 2


def test_channel_dimensions(short_reference_data_path: Path, new_dlis_path: Path):
    """Test that dimensions for the channels in DLIS are stored correctly."""

    write_time_based_dlis(new_dlis_path, data=short_reference_data_path)

    with load_dlis(new_dlis_path) as f:
        def check(name, shape):
            ch = select_channel(f, name)
            assert ch.dimension == shape
            assert ch.element_limit == shape

        check('posix time', [1])
        check('surface rpm', [1])
        check('amplitude', [128])
        check('radius', [128])
        check('radius_pooh', [128])


@pytest.mark.parametrize('n_points', (10, 100, 128, 987))
def test_channel_curves(reference_data_path: Path, reference_data: h5py.File, new_dlis_path: Path, n_points: int,
                        config_array_time_based: ConfigParser, config_time_based: ConfigParser):
    """Create a DLIS file with varying number of points. Check that the data for each channel are correct."""

    write_time_based_dlis(new_dlis_path, data=reference_data_path, to_idx=n_points)

    with load_dlis(new_dlis_path) as f:
        for name in ('posix time', 'surface rpm'):
            curve = select_channel(f, name).curves()
            assert curve.shape == (n_points,)

        for name in ('amplitude', 'radius', 'radius_pooh'):
            curve = select_channel(f, name).curves()
            assert curve.shape == (n_points, N_COLS)

        def check_contents(channel_name, data_name):
            curve = select_channel(f, channel_name).curves()
            data = reference_data[data_name][:n_points]
            assert pytest.approx(curve) == data

        check_contents('posix time', '/contents/time')
        check_contents('surface rpm', '/contents/rpm')
        check_contents('amplitude', '/contents/image0')
        check_contents('radius', '/contents/image1')
        check_contents('radius_pooh', '/contents/image2')

