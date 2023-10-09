import os
import pytest

from datetime import datetime

from dlis_writer.utils.loaders import load_config
from dlis_writer.writer.mwe_dlis_creation import write_dlis_file

from dlis_writer.tests.test_writer.common import base_data_path, reference_data, short_reference_data  # fixtures
from dlis_writer.tests.test_writer.common import N_COLS, load_dlis, select_channel, make_channels  # constants and functions


@pytest.fixture(scope='session')
def config_params(base_data_path):
    return load_config(base_data_path/'resources/mock_config_params.ini')


@pytest.fixture(scope='session')
def short_dlis(short_reference_data, base_data_path, config_params):
    dlis_path = base_data_path/'outputs/new_fake_dlis_shared.DLIS'

    write_dlis_file(
        data=short_reference_data,
        channels=make_channels(),
        dlis_file_name=dlis_path,
        config=config_params
    )

    with load_dlis(dlis_path) as f:
        yield f

    if dlis_path.exists():  # does not exist if file creation failed
        os.remove(dlis_path)


def test_channel_properties(short_dlis, config_params):
    for name in ('posix time', 'surface rpm'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [1]
        assert chan.dimension == [1]

    for name in ('amplitude', 'radius', 'radius_pooh'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [N_COLS]
        assert chan.dimension == [N_COLS]

    assert short_dlis.object("CHANNEL", 'amplitude').units is None
    assert short_dlis.object("CHANNEL", 'radius').units == "inch"
    assert short_dlis.object("CHANNEL", 'radius_pooh').units == "meter"


def test_file_header(short_dlis, config_params):
    header = short_dlis.fileheader
    assert header.id == config_params['FileHeader']['name']
    assert header.sequencenr == config_params['FileHeader']['sequence_number']


def test_origin(short_dlis, config_params):
    assert len(short_dlis.origins) == 1

    origin = short_dlis.origins[0]
    conf = config_params['Origin.attributes']

    assert origin.name == config_params['Origin']['name']
    assert origin.creation_time == datetime.strptime(conf['creation_time'], "%Y/%m/%d %H:%M:%S")
    assert origin.file_id == conf['file_id']
    assert origin.file_set_name == conf['file_set_name']
    assert origin.file_set_nr == int(conf['file_set_number'])
    assert origin.file_nr == int(conf['file_number'])
    assert origin.run_nr == [int(conf['run_number'])]
    assert origin.well_id == int(conf['well_id'])
    assert origin.well_name == conf['well_name']
    assert origin.field_name == conf['field_name']
    assert origin.company == conf['company']

    # not set - absent from config
    assert origin.producer_name is None
    assert origin.product is None
    assert origin.order_nr is None
    assert origin.version is None
    assert origin.programs == []


def test_frame(short_dlis, config_params):
    assert len(short_dlis.frames) == 1

    frame = short_dlis.frames[0]

    assert frame.name == config_params['Frame']['name']
    assert frame.index_type == config_params['Frame.attributes']['index_type']


def test_storage_unit_label(short_dlis, config_params):
    sul = short_dlis.storage_label()
    assert sul['id'].rstrip(' ') == config_params['StorageUnitLabel']['name']
    assert sul['sequence'] == int(config_params['StorageUnitLabel']['sequence_number'])
    assert sul['maxlen'] == 8192

