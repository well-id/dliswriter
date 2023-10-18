import pytest
from datetime import datetime

from dlis_writer.logical_record.eflr_types import CalibrationMeasurement, Channel, Axis
from dlis_writer.utils.enums import Units, RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params, make_config


def test_calibration_measurement_from_config(config_params):
    key = "CalibrationMeasurement-1"
    m = CalibrationMeasurement.from_config(config_params, key=key)

    assert m.object_name == "CMEASURE-1"
    assert m.phase.value == 'BEFORE'
    assert isinstance(m.measurement_source.value, Channel)
    assert m.measurement_source.value.object_name == "Channel 1"
    assert m._type.value == 'Plus'
    assert isinstance(m.axis.value[0], Axis)
    assert m.axis.value[0].object_name == 'Axis-1'
    assert m.measurement.value == [12.2323]
    assert m.sample_count.value == [12]
    assert m.maximum_deviation.value == [2.2324]
    assert isinstance(m.begin_time.value, datetime)
    assert m.begin_time.value == datetime(2050, 3, 12, 12, 30)
    assert m.duration.value == 15
    assert m.duration.units is Units.s
    assert m.reference.value == [11]
    assert m.standard.value == [11.2]
    assert m.plus_tolerance.value == [2]
    assert m.minus_tolerance.value == [1]

