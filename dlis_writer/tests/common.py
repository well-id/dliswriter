import pytest
from pathlib import Path
from contextlib import contextmanager
from dlisio import dlis

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units


N_COLS = 128
SHORT_N_ROWS = 100


@pytest.fixture(scope='session')
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def reference_data(base_data_path):
    return load_hdf5(base_data_path / 'resources/mock_data.hdf5')


@pytest.fixture(scope='session')
def short_reference_data(reference_data):
    return reference_data[:SHORT_N_ROWS]


@contextmanager
def load_dlis(fname):
    with dlis.load(fname) as (f, *tail):
        try:
            yield f
        finally:
            pass


def select_channel(f, name):
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


def make_channels(include_images=True, repr_code=RepresentationCode.FSINGL, depth_based=False):
    rc = RepresentationCode.FDOUBL
    if depth_based:
        index_channel = Channel.create('depth', unit='m', repr_code=rc)
    else:
        index_channel = Channel.create('posix time', unit='s', repr_code=rc, dataset_name='time')

    rpm_channel = _make_rpm_channel()

    if not include_images:
        return [index_channel, rpm_channel]
    return [index_channel, rpm_channel] + _make_image_channels(repr_code=repr_code)

