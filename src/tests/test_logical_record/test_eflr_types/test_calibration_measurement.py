from datetime import datetime
import pytest

from dlis_writer import AttrSetup, enums, high_compatibility_mode_decorator
from dlis_writer.logical_record.eflr_types import (AxisItem, ChannelItem, CalibrationMeasurementItem,
                                                   CalibrationMeasurementSet)


def test_calibration_measurement_creation(channel1: ChannelItem, axis1: AxisItem) -> None:
    m = CalibrationMeasurementItem(
        "CMEASURE-1",
        **{
            'phase': enums.CalibrationMeasurementPhase.BEFORE,
            'measurement_source': channel1,
            'type': 'Plus',
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
    assert m.type.value == 'Plus'
    assert isinstance(m.axis.value[0], AxisItem)
    assert m.axis.value[0].name == 'Axis-1'
    assert m.measurement.value == [12.2323]
    assert m.sample_count.value == 12
    assert m.maximum_deviation.value == [2.2324]
    assert isinstance(m.begin_time.value, datetime)
    assert m.begin_time.value == datetime(2050, 3, 12, 12, 30)
    assert m.duration.value == 15
    assert m.duration.units == 's'
    assert m.reference.value == [11]
    assert m.standard.value == [11.2]
    assert m.plus_tolerance.value == [2]
    assert m.minus_tolerance.value == [1]


@pytest.mark.parametrize("t", ("PLUS", "TWO-POINT-LINEAR", "A3"))
@high_compatibility_mode_decorator
def test_type_compatible(t: str) -> None:
    CalibrationMeasurementItem("CM-1", type=t, parent=CalibrationMeasurementSet())


@pytest.mark.parametrize("t", ("Plus", "type 2", "T.1"))
@high_compatibility_mode_decorator
def test_type_not_compatible(t: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        CalibrationMeasurementItem("CM-1", type=t, parent=CalibrationMeasurementSet())


@pytest.mark.parametrize("name", ("CMEAS-1", "MEASUREMENT_3", "M11"))
@high_compatibility_mode_decorator
def test_name_compatible(name: str) -> None:
    CalibrationMeasurementItem(name, parent=CalibrationMeasurementSet())


@pytest.mark.parametrize("name", ("Meas1", "M.1", "M TYPE 2"))
@high_compatibility_mode_decorator
def test_label_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        CalibrationMeasurementItem(name, parent=CalibrationMeasurementSet())
