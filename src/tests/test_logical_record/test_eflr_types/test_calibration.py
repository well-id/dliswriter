from datetime import datetime

from dlis_writer import AttrSetup
from dlis_writer.logical_record.core.attribute import EFLRAttribute
from dlis_writer.logical_record.eflr_types import (AxisItem, ChannelItem, ParameterItem, CalibrationMeasurementItem,
                                                   CalibrationCoefficientItem, CalibrationItem, CalibrationSet,
                                                   CalibrationCoefficientSet, CalibrationMeasurementSet)


def test_calibration_measurement_creation(channel1: ChannelItem, axis1: AxisItem) -> None:
    m = CalibrationMeasurementItem(
        "CMEASURE-1",
        **{
            'phase': 'BEFORE',
            'measurement_source': channel1,
            '_type': 'Plus',
            'axis': axis1,
            'measurement': AttrSetup(12.2323),
            'sample_count': {'value': 12},
            'maximum_deviation': 2.2324,
            'begin_time': '2050/03/12 12:30:00',
            'duration': AttrSetup(15, 's'),
            'reference': [11],
            'standard': [11.2],
            'plus_tolerance': [2],
            'minus_tolerance': AttrSetup(value=1),
        },
        parent=CalibrationMeasurementSet()
    )

    assert m.name == "CMEASURE-1"
    assert m.phase.value == 'BEFORE'
    assert isinstance(m.measurement_source.value, ChannelItem)
    assert m.measurement_source.value.name == "Channel 1"
    assert m._type.value == 'Plus'
    assert isinstance(m.axis.value[0], AxisItem)
    assert m.axis.value[0].name == 'Axis-1'
    assert m.measurement.value == [12.2323]
    assert m.sample_count.value == 12
    assert m.maximum_deviation.value == 2.2324
    assert isinstance(m.begin_time.value, datetime)
    assert m.begin_time.value == datetime(2050, 3, 12, 12, 30)
    assert m.duration.value == 15
    assert m.duration.units == 's'
    assert m.reference.value == [11]
    assert m.standard.value == [11.2]
    assert m.plus_tolerance.value == [2]
    assert m.minus_tolerance.value == [1]


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


def _check_list(objects: EFLRAttribute, names: tuple[str, ...], object_class: type) -> None:
    """Check that the objects defined for a given EFLR attribute match the expected names and type."""

    objects_list = objects.value

    assert isinstance(objects_list, list)
    assert len(objects_list) == len(names)
    for i, name in enumerate(names):
        assert isinstance(objects_list[i], object_class)
        assert objects_list[i].name == name


def test_calibration_creation(channel1: ChannelItem, channel2: ChannelItem, channel3: ChannelItem,
                              ccoef1: CalibrationCoefficientItem, cmeasure1: CalibrationMeasurementItem,
                              param1: ParameterItem, param2: ParameterItem, param3: ParameterItem) -> None:
    """Check that a CalibrationObject is correctly set up from config info."""

    c = CalibrationItem(
        "CALIB-MAIN",
        calibrated_channels=(channel1, channel2),
        uncalibrated_channels=(channel3,),
        coefficients=(ccoef1,),
        measurements=(cmeasure1,),
        parameters=(param1, param2, param3),
        parent=CalibrationSet()
    )

    assert c.name == "CALIB-MAIN"

    _check_list(c.calibrated_channels, ("Channel 1", "Channel 2"), ChannelItem)
    _check_list(c.uncalibrated_channels, ("Channel 3",), ChannelItem)
    _check_list(c.coefficients, ("COEF-1",), CalibrationCoefficientItem)
    _check_list(c.measurements, ("CMEASURE-1",), CalibrationMeasurementItem)
    _check_list(c.parameters, ("Param-1", "Param-2", "Param-3"), ParameterItem)
