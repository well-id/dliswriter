import pytest

from dlis_writer.logical_record.eflr_types.parameter import ParameterSet, ParameterItem
from dlis_writer.utils.enums import RepresentationCode


@pytest.mark.parametrize(("name", "value", "value_type", "n_values", "repr_code"), (
        ("p1", ["ahaha", "abc"], str, 2, RepresentationCode.ASCII),
        ("some param", [2.33, 2.1], float, 2, RepresentationCode.FDOUBL),
        ("p89", -12.1211, float, 1, RepresentationCode.FDOUBL)
))
def test_from_config(name, value, value_type: type, n_values: int, repr_code: RepresentationCode):
    """Test creating ParameterItem."""

    param = ParameterItem(name, values=value)

    assert param.name == name

    assert param.values.representation_code is repr_code
    assert isinstance(param.values.value, list)
    assert all(isinstance(v, value_type) for v in param.values.value)
    assert len(param.values.value) == n_values

    assert isinstance(param.parent, ParameterSet)
    assert param.parent.set_name is None
