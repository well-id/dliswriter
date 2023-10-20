import pytest

from dlis_writer.logical_record.eflr_types import Parameter
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize(("param_nr", "value_type", "n_values", "repr_code"), (
        (1, str, 2, RepresentationCode.ASCII),
        (2, float, 2, RepresentationCode.FDOUBL),
        (3, float, 1, RepresentationCode.FDOUBL)
))
def test_from_config(config_params, param_nr, value_type, n_values, repr_code):
    key = f"Parameter-{param_nr}"
    param = Parameter.make_from_config(config_params, key=key)
    
    conf = config_params[key]
    
    assert param.object_name == conf['name']
    assert param.long_name.value == conf['long_name']

    assert param.values.representation_code is repr_code
    assert isinstance(param.values.value, list)
    assert all(isinstance(v, value_type) for v in param.values.value)
    assert len(param.values.value) == n_values
