from datetime import datetime, timezone
from dlisio import dlis    # type: ignore  # untyped library

from tests.common import check_list_of_objects


def test_calibration_measurement_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of CalibrationMeasurement object in the DLIS file."""

    m = short_dlis.measurements[0]

    assert m.name == "CMEASURE-1"
    assert m.phase == 'BEFORE'
    assert m.axis[0].name == 'Axis-4'
    assert m.source.name == "Channel 1"
    assert m.mtype == 'Plus'
    assert m.samples.tolist() == [[12.2323, 12.2131]]
    assert m.samplecount == 12
    assert m.max_deviation.tolist() == [2.2324, 3.121]
    assert m.begin_time.replace(tzinfo=timezone.utc) == datetime(2050, 3, 12, 12, 30).astimezone(timezone.utc)
    assert m.duration == 15
    assert m.reference.tolist() == [11, 12]
    assert m.standard == [11.2, 12.2]
    assert m.plus_tolerance.tolist() == [2, 2]
    assert m.minus_tolerance.tolist() == [1, 2]
    assert m.origin == 42
    assert m.dimension == [2]


def test_calibration_coefficient_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of CalibrationCoefficient object in the DLIS file."""

    c = short_dlis.coefficients[0]

    assert c.name == "COEF-1"
    assert c.label == 'Gain'
    assert c.coefficients == [100.2, 201.3]
    assert c.references == [89, 298]
    assert c.plus_tolerance == [100.2, 222.124]
    assert c.minus_tolerance == [87.23, 214]
    assert c.origin == 42


def test_calibration_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Calibration object in the DLIS file."""

    c = short_dlis.calibrations[0]

    assert c.name == 'CALIB-MAIN'
    assert c.origin == 42

    check_list_of_objects(c.calibrated, ("Channel 1", "Channel 2"))
    check_list_of_objects(c.uncalibrated, ("amplitude", "radius", "radius_pooh"))
    check_list_of_objects(c.coefficients, ("COEF-1",))
    check_list_of_objects(c.measurements, ("CMEASURE-1",))
    check_list_of_objects(c.parameters, ("Param-1", "Param-2", "Param-3"))
