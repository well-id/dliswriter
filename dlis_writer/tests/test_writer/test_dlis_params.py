import os
import pytest
from datetime import datetime

from dlis_writer.utils.enums import RepresentationCode, Units
from dlis_writer.tests.common import base_data_path, config_params
from dlis_writer.tests.test_writer.common import reference_data, short_reference_data
from dlis_writer.tests.test_writer.common import N_COLS, load_dlis, select_channel, write_dlis_file


@pytest.fixture(scope='session')
def short_dlis(short_reference_data, base_data_path, config_params):
    dlis_path = base_data_path/'outputs/new_fake_dlis_shared.DLIS'

    channel_names = [f"Channel-{s}" for s in ("time", "rpm", "amplitude", "radius", "radius_pooh")]
    config_params['Frame']['channels'] = ', '.join(channel_names)

    write_dlis_file(data=short_reference_data, dlis_file_name=dlis_path, config=config_params)

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
    conf = config_params['Origin']

    assert origin.name == conf['name']
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
    assert frame.index_type == config_params['Frame']['index_type']


def test_storage_unit_label(short_dlis, config_params):
    sul = short_dlis.storage_label()
    assert sul['id'].rstrip(' ') == config_params['StorageUnitLabel']['name']
    assert sul['sequence'] == int(config_params['StorageUnitLabel']['sequence_number'])
    assert sul['maxlen'] == 8192


def test_zones(short_dlis):
    zones = short_dlis.zones
    assert len(zones) == 4


@pytest.mark.parametrize(("idx", "name", "description", "maximum", "minimum", "value_type"), (
        (0, "Zone-1", "BOREHOLE-DEPTH-ZONE", 1300, 100, int),
        (1, "Zone-2", "VERTICAL-DEPTH-ZONE", 2300.45, 200, float),
        (2, "Zone-3", "ZONE-TIME", datetime(2050, 7, 13, 11, 30), datetime(2050, 7, 12, 9), datetime),
        (3, "Zone-4", "ZONE-TIME-2", 90, 10, int)
))
def test_zone_params(short_dlis, idx, name, description, maximum, minimum, value_type):
    z = short_dlis.zones[idx]
    assert z.name == name
    assert z.description == description

    assert z.maximum == maximum
    assert z.minimum == minimum
    assert isinstance(z.maximum, value_type)
    assert isinstance(z.minimum, value_type)


def test_parameters(short_dlis):
    params = short_dlis.parameters
    assert len(params) == 3


@pytest.mark.parametrize(("idx", "name", "long_name", "values", "zones"), (
        (0, "Param-1", "LATLONG-GPS", ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"], ["Zone-1", "Zone-3"]),
        (1, "Param-2", "LATLONG", [40.395241, 27.792471], ["Zone-2", "Zone-4"]),
        (2, "Param-3", "SOME-FLOAT-PARAM", [12.5], [])
))
def test_parameters_params(short_dlis, idx, name, long_name, values, zones):
    param = short_dlis.parameters[idx]
    assert param.name == name
    assert param.long_name == long_name
    assert param.values.tolist() == values

    assert len(param.zones) == len(zones)
    for i, z in enumerate(zones):
        assert param.zones[i].name == z