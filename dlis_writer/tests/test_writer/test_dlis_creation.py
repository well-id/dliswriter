import os
import pytest

from dlis_writer.utils.loaders import load_config
from dlis_writer.writer.utils.compare_dlis_files import compare
from dlis_writer.utils.enums import RepresentationCode, Units

from dlis_writer.tests.test_writer.common import base_data_path, reference_data, short_reference_data  # fixtures
from dlis_writer.tests.test_writer.common import N_COLS, load_dlis, select_channel, write_dlis_file
from dlis_writer.tests.common import clear_eflr_instance_registers


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


@pytest.fixture
def new_dlis_path(base_data_path):
    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


def test_correct_contents_rpm_only_depth_based(reference_data, base_data_path, new_dlis_path, config_depth_based):
    write_dlis_file(data=reference_data, dlis_file_name=new_dlis_path, config=config_depth_based)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_rpm_depth_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_correct_contents_rpm_and_images_time_based(reference_data, base_data_path, new_dlis_path, config_time_based):
    write_dlis_file(data=reference_data, dlis_file_name=new_dlis_path, config=config_time_based)

    reference_dlis_path = base_data_path / 'resources/reference_dlis_full_time_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


@pytest.mark.parametrize('include_images', (True, False))
def test_dlis_depth_based(short_reference_data, new_dlis_path, include_images, config_depth_based):
    write_dlis_file(data=short_reference_data, dlis_file_name=new_dlis_path, config=config_depth_based)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'depth'
        assert chan.units == Units.m.value
        assert chan.reprc == 7

        assert f.frames[0].index_type == 'DEPTH'


def test_dlis_time_based(short_reference_data, new_dlis_path, config_time_based):
    write_dlis_file(data=short_reference_data, dlis_file_name=new_dlis_path, config=config_time_based)

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'posix time'
        assert chan.units == Units.s.value
        assert chan.reprc == 7

        assert f.frames[0].index_type == 'TIME'


@pytest.mark.parametrize(("code", "value"), ((RepresentationCode.FSINGL, 2), (RepresentationCode.FDOUBL, 7)))
def test_repr_code(short_reference_data, new_dlis_path, code, value, config_time_based):
    for name in config_time_based.sections():
        if name.startswith('Channel'):
            config_time_based[name]['representation_code'] = str(code.value)

    write_dlis_file(data=short_reference_data, dlis_file_name=new_dlis_path, config=config_time_based)

    with load_dlis(new_dlis_path) as f:
        for name in ('amplitude', 'radius', 'radius_pooh'):
            chan = select_channel(f, name)
            assert chan.reprc == value


@pytest.mark.parametrize('n_points', (10, 100, 128, 987))
def test_channel_curves(reference_data, new_dlis_path, n_points, config_time_based):
    write_dlis_file(data=reference_data[:n_points], dlis_file_name=new_dlis_path, config=config_time_based)

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

        check_contents('posix time', 'time')
        check_contents('surface rpm', 'rpm')
        check_contents('amplitude', 'image0')
        check_contents('radius', 'image1')
        check_contents('radius_pooh', 'image2')

