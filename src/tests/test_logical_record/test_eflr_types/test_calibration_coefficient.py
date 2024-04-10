import pytest

from dlis_writer import high_compatibility_mode_decorator
from dlis_writer.logical_record.eflr_types import CalibrationCoefficientItem, CalibrationCoefficientSet


def test_calibration_coefficient_creation() -> None:
    """Check that a CalibrationCoefficientObject is correctly set up from config info."""

    c = CalibrationCoefficientItem(
        'COEF-1',
        label='Gain',
        coefficients=[100.2, 201.3],
        references=[89, 298],
        plus_tolerances=[100.2, 222.124],
        minus_tolerances=[87.23, 214],
        parent=CalibrationCoefficientSet()
    )

    assert c.name == "COEF-1"
    assert c.label.value == 'Gain'
    assert c.coefficients.value == [100.2, 201.3]
    assert c.references.value == [89, 298]
    assert c.plus_tolerances.value == [100.2, 222.124]
    assert c.minus_tolerances.value == [87.23, 214]


def test_calibration_coefficient_unequal_counts() -> None:

    c = CalibrationCoefficientItem(
        'CX',
        label='Offset',
        coefficients=[100.2, 201.3],
        references=[89, 298, 21],
        plus_tolerances=[100.2, 222.124],
        parent=CalibrationCoefficientSet()
    )

    with pytest.raises(RuntimeError,
                       match="Number of values all numeric attributes of Calibration Coefficient should be equal; "
                             "got 2 for COEFFICIENTS, 3 for REFERENCES, 2 for PLUS-TOLERANCES"):
        c.make_item_body_bytes()


@pytest.mark.parametrize("label", ("CCOEF-1", "COEFFICIENT_3", "3112-1212"))
@high_compatibility_mode_decorator
def test_ccoef_label_compatible(label: str) -> None:
    CalibrationCoefficientItem("CC-1", label=label, parent=CalibrationCoefficientSet())


@pytest.mark.parametrize("label", ("Calibration coefficient", "CALIB C0EFF-3", "C@2"))
@high_compatibility_mode_decorator
def test_ccoef_label_not_compatible(label: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        CalibrationCoefficientItem("CC-1", label=label, parent=CalibrationCoefficientSet())


@pytest.mark.parametrize("name", ("CCOEF-1", "COEFFICIENT_3", "C12"))
@high_compatibility_mode_decorator
def test_ccoef_name_compatible(name: str) -> None:
    CalibrationCoefficientItem(name, parent=CalibrationCoefficientSet())


@pytest.mark.parametrize("name", ("Coefficient", "C0EFF 3", "C.12"))
@high_compatibility_mode_decorator
def test_ccoef_name_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        CalibrationCoefficientItem(name, parent=CalibrationCoefficientSet())
