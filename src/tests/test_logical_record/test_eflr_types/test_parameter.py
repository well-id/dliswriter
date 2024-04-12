import pytest
from typing import Any

from dliswriter.logical_record.eflr_types.parameter import ParameterSet, ParameterItem
from dliswriter.utils.internal_enums import RepresentationCode


@pytest.mark.parametrize(("name", "value", "value_type", "n_values", "repr_code"), (
        ("p1", ["ahaha", "abc"], str, 2, RepresentationCode.ASCII),
        ("some param", [2.33, 2.1], float, 2, RepresentationCode.FDOUBL),
        ("p89", -12.1211, float, 1, RepresentationCode.FDOUBL)
))
def test_from_config(name: str, value: Any, value_type: type, n_values: int, repr_code: RepresentationCode) -> None:
    """Test creating ParameterItem."""

    param = ParameterItem(name, values=value, parent=ParameterSet())

    assert param.name == name

    assert param.values.representation_code is repr_code
    assert isinstance(param.values.value, list)
    assert all(isinstance(v, value_type) for v in param.values.value)
    assert len(param.values.value) == n_values

    assert isinstance(param.parent, ParameterSet)
    assert param.parent.set_name is None
