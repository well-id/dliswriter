from datetime import datetime

from dlis_writer.logical_record.eflr_types import Origin
from dlis_writer.tests.common import base_data_path, config_params


def test_from_config(config_params):
    origin = Origin.from_config(config_params)

    conf = config_params['Origin.attributes']

    assert origin.object_name == config_params['Origin']['name']

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


