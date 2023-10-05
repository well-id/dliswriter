import os
import pytest
from pathlib import Path

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.tests.utils.mwe_dlis_creation import write_dlis_file
from dlis_writer.tests.utils.compare_dlis_files import compare
from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units


N_COLS = 128


@pytest.fixture
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture
def reference_data(base_data_path):
    return load_hdf5(base_data_path / 'resources/mock_data.hdf5')


@pytest.fixture
def new_dlis_path(base_data_path):
    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


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


def test_correct_contents_rpm_only_depth_based(reference_data, base_data_path, new_dlis_path):
    write_dlis_file(
        data=reference_data,
        channels=[_make_rpm_channel()],
        dlis_file_name=new_dlis_path,
        depth_based=True
    )

    reference_dlis_path = base_data_path / 'resources/reference_dlis_rpm_depth_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)


def test_correct_contents_rpm_and_images_time_based(reference_data, base_data_path, new_dlis_path):
    write_dlis_file(
        data=reference_data,
        channels=[_make_rpm_channel()] + _make_image_channels(),
        dlis_file_name=new_dlis_path,
        depth_based=False
    )

    reference_dlis_path = base_data_path / 'resources/reference_dlis_full_time_based.DLIS'
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)
