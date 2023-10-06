import os
import pytest
from pathlib import Path
from contextlib import contextmanager
from dlisio import dlis

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.tests.utils.mwe_dlis_creation import write_dlis_file
from dlis_writer.tests.utils.compare_dlis_files import compare
from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units


N_COLS = 128
SHORT_N_ROWS = 100


@pytest.fixture
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture
def reference_data(base_data_path):
    return load_hdf5(base_data_path / 'resources/mock_data.hdf5')


@pytest.fixture
def short_reference_data(reference_data):
    return reference_data[:SHORT_N_ROWS]


@pytest.fixture
def new_dlis_path(base_data_path):
    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


@contextmanager
def load_dlis(fname):
    with dlis.load(fname) as (f, *tail):
        try:
            yield f
        finally:
            pass


def _select_channel(f, name):
    return f.object("CHANNEL", name)


def _make_rpm_channel():
    return Channel.create('surface rpm', unit='rpm', dataset_name='rpm')


def _make_image_channels(repr_code=RepresentationCode.FSINGL, n=3):
    def make_channel(name, **kwargs):
        return Channel.create(name, **kwargs, element_limit=N_COLS, dimension=N_COLS, repr_code=repr_code)

    channels = [
        make_channel('amplitude', unit=None, dataset_name='image0'),
        make_channel('radius', unit=Units.in_, dataset_name='image1'),
        make_channel('radius_pooh', unit=Units.m, dataset_name='image2'),
    ]

    return channels[:n]


def _make_channels(include_images=True, repr_code=RepresentationCode.FSINGL):
    rpm_channel = _make_rpm_channel()
    if not include_images:
        return [rpm_channel]
    return [rpm_channel] + _make_image_channels(repr_code=repr_code)


def test_correct_contents_rpm_only_depth_based(reference_data, base_data_path, new_dlis_path):
    write_dlis_file(
        data=reference_data,
        channels=_make_channels(include_images=False),
        dlis_file_name=new_dlis_path,
        depth_based=True
    )

    reference_dlis_path = base_data_path / 'resources/reference_dlis_rpm_depth_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_correct_contents_rpm_and_images_time_based(reference_data, base_data_path, new_dlis_path):
    write_dlis_file(
        data=reference_data,
        channels=_make_channels(),
        dlis_file_name=new_dlis_path,
        depth_based=False
    )

    reference_dlis_path = base_data_path / 'resources/reference_dlis_full_time_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


@pytest.mark.parametrize('include_images', (True, False))
def test_dlis_depth_based(short_reference_data, new_dlis_path, include_images):
    write_dlis_file(
        data=short_reference_data,
        channels=_make_channels(include_images=include_images),
        dlis_file_name=new_dlis_path,
        depth_based=True
    )

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'depth'
        assert chan.units == 'm'
        assert chan.reprc == 7


def test_dlis_time_based(short_reference_data, new_dlis_path):
    write_dlis_file(
        data=short_reference_data,
        channels=_make_channels(include_images=False),
        dlis_file_name=new_dlis_path,
        depth_based=False
    )

    with load_dlis(new_dlis_path) as f:
        chan = f.channels[0]
        assert chan.name == 'posix time'
        assert chan.units == 's'
        assert chan.reprc == 7


@pytest.mark.parametrize(("code", "value"), ((RepresentationCode.FSINGL, 2), (RepresentationCode.FDOUBL, 7)))
def test_repr_code(short_reference_data, new_dlis_path, code, value):
    write_dlis_file(
        data=short_reference_data,
        channels=_make_channels(repr_code=code),
        dlis_file_name=new_dlis_path
    )

    with load_dlis(new_dlis_path) as f:
        for name in ('amplitude', 'radius', 'radius_pooh'):
            chan = _select_channel(f, name)
            assert chan.reprc == value


def test_channel_properties(short_reference_data, new_dlis_path):
    write_dlis_file(
        data=short_reference_data,
        channels=_make_channels(),
        dlis_file_name=new_dlis_path
    )

    with load_dlis(new_dlis_path) as f:

        for name in ('posix time', 'surface rpm'):
            chan = _select_channel(f, name)
            assert chan.name == name
            assert chan.element_limit == [1]
            assert chan.dimension == [1]

        for name in ('amplitude', 'radius', 'radius_pooh'):
            chan = _select_channel(f, name)
            assert chan.name == name
            assert chan.element_limit == [N_COLS]
            assert chan.dimension == [N_COLS]

        assert f.object("CHANNEL", 'amplitude').units is None
        assert f.object("CHANNEL", 'radius').units == "inch"
        assert f.object("CHANNEL", 'radius_pooh').units == "meter"


@pytest.mark.parametrize('n_points', (10, 100, 128, 987))
def test_channel_curves(reference_data, new_dlis_path, n_points):
    write_dlis_file(
        data=reference_data[:n_points],
        channels=_make_channels(),
        dlis_file_name=new_dlis_path
    )

    with load_dlis(new_dlis_path) as f:
        for name in ('posix time', 'surface rpm'):
            curve = _select_channel(f, name).curves()
            assert curve.shape == (n_points,)

        for name in ('amplitude', 'radius', 'radius_pooh'):
            curve = _select_channel(f, name).curves()
            assert curve.shape == (n_points, N_COLS)
