import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.parameter import ParameterTable, ParameterItem
from dlis_writer.utils.enums import RepresentationCode

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("param_nr", "value_type", "n_values", "repr_code"), (
        (1, str, 2, RepresentationCode.ASCII),
        (2, float, 2, RepresentationCode.FDOUBL),
        (3, float, 1, RepresentationCode.FDOUBL)
))
def test_from_config(config_params: ConfigParser, param_nr: int, value_type: type, n_values: int,
                     repr_code: RepresentationCode):

    """Test creating ParameterObject from config."""

    key = f"Parameter-{param_nr}"
    param: ParameterItem = ParameterTable.make_eflr_item_from_config(config_params, key=key)
    
    conf = config_params[key]
    
    assert param.name == conf['name']
    assert param.long_name.value == conf['long_name']

    assert param.values.representation_code is repr_code
    assert isinstance(param.values.value, list)
    assert all(isinstance(v, value_type) for v in param.values.value)
    assert len(param.values.value) == n_values
