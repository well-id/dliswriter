import os
import pytest
from copy import deepcopy

from dlis_writer.writer.dlis_config import load_config
from dlis_writer.writer.dlis_file_comparator import compare
from dlis_writer.utils.enums import RepresentationCode

from dlis_writer.tests.test_writer.common import base_data_path, reference_data_path, reference_data, short_reference_data, short_reference_data_path  # fixtures
from dlis_writer.tests.test_writer.common import N_COLS, load_dlis, select_channel, write_file
from dlis_writer.tests.common import clear_eflr_instance_registers
from dlis_writer.utils.source_data_objects import HDF5Interface


@pytest.fixture(autouse=True)
def cleanup():
    clear_eflr_instance_registers()
    yield


@pytest.fixture(scope='session')
def config_depth_based(base_data_path):
    return load_config(base_data_path/'resources/mock_config_depth_based.ini')


@pytest.fixture(scope='session')
def config_time_based(base_data_path):
    return load_config(base_data_path/'resources/mock_config_time_based.ini')


@pytest.fixture(scope='session')
def config_array_time_based(config_time_based):
    c = deepcopy(config_time_based)
    for s in c.sections():
        if s.startswith('Channel'):
            if 'dataset_name' in c[s].keys():
                c[s]['dataset_name'] = c[s]['name']

    return c


@pytest.fixture
def new_dlis_path(base_data_path):
    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


def test_correct_contents_rpm_only_depth_based(reference_data_path, base_data_path, new_dlis_path, config_depth_based):
    write_file(data=reference_data_path, dlis_file_name=new_dlis_path, config=config_depth_based)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_rpm_depth_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_correct_contents_rpm_and_images_time_based(reference_data_path, base_data_path, new_dlis_path, config_time_based):
    write_file(data=reference_data_path, dlis_file_name=new_dlis_path, config=config_time_based)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_full_time_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


@pytest.mark.parametrize('include_images', (True, False))
def test_dlis_depth_based(short_reference_data, short_reference_data_path, new_dlis_path, include_images, config_depth_based):
    write_file(data=short_reference_data_path, dlis_file_name=new_dlis_path, config=config_depth_based)

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


def test_dlis_time_based(short_reference_data, short_reference_data_path, new_dlis_path, config_time_based):
    write_file(data=short_reference_data_path, dlis_file_name=new_dlis_path, config=config_time_based)

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


@pytest.mark.parametrize(("code", "value"), ((RepresentationCode.FSINGL, 2), (RepresentationCode.FDOUBL, 7)))
def test_repr_code(short_reference_data_path, new_dlis_path, code, value, config_time_based):
    for name in config_time_based.sections():
        if name.startswith('Channel'):
            config_time_based[name]['representation_code'] = str(code.value)

    write_file(data=short_reference_data_path, dlis_file_name=new_dlis_path, config=config_time_based)

    with load_dlis(new_dlis_path) as f:
        for name in ('amplitude', 'radius', 'radius_pooh'):
            chan = select_channel(f, name)
            assert chan.reprc == value


@pytest.mark.parametrize('n_points', (10, 100, 128, 987))
def test_channel_curves(reference_data_path, reference_data, new_dlis_path, n_points, config_array_time_based, config_time_based):
    data = HDF5Interface.from_config(reference_data_path, config_time_based)
    write_file(data=data.load_chunk(0, n_points), dlis_file_name=new_dlis_path, config=config_array_time_based)

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

