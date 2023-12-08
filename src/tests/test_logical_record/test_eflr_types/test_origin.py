from datetime import datetime, timedelta
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.origin import OriginItem, OriginTable

from tests.common import base_data_path, config_params, make_config


def test_from_config(config_params: ConfigParser):
    """Test creating OriginObject from config."""

    origin: OriginItem = OriginTable.make_object_from_config(config_params)

    conf = config_params['Origin']

    assert origin.name == conf['name']

    assert origin.creation_time.value == datetime.strptime(conf['creation_time'], "%Y/%m/%d %H:%M:%S")
    assert origin.file_id.value == conf['file_id']
    assert origin.file_set_name.value == conf['file_set_name']
    assert origin.file_set_number.value == int(conf['file_set_number'])
    assert origin.file_number.value == int(conf['file_number'])
    assert origin.run_number.value == int(conf['run_number'])
    assert origin.well_id.value == int(conf['well_id'])
    assert origin.well_name.value == conf['well_name']
    assert origin.field_name.value == conf['field_name']
    assert origin.company.value == conf['company']

    # not set - absent from config
    assert origin.producer_name.value is None
    assert origin.product.value is None
    assert origin.order_number.value is None
    assert origin.version.value is None
    assert origin.programs.value is None


def test_from_config_no_dtime_in_attributes():
    """Test that if creation_time is missing from config, the origin gets the current date and time as creation time."""

    config = make_config("Origin")
    config['Origin']['name'] = "Some origin name"
    config['Origin']['well_name'] = "Some well name"

    origin: OriginItem = OriginTable.make_object_from_config(config)
    assert origin.name == "Some origin name"
    assert origin.well_name.value == "Some well name"

    assert timedelta(seconds=0) <= datetime.now() - origin.creation_time.value < timedelta(seconds=1)


def test_from_config_no_attributes():
    """Test creating OriginObject from config with minimum number of parameters."""

    config = make_config("Origin")
    config['Origin']['name'] = "Some origin name"

    origin: OriginItem = OriginTable.make_object_from_config(config)
    assert origin.name == "Some origin name"
    assert origin.well_name.value is None

    assert timedelta(seconds=0) <= datetime.now() - origin.creation_time.value < timedelta(seconds=1)
