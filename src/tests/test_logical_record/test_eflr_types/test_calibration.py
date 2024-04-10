from dlis_writer.logical_record.core.attribute import EFLRAttribute
from dlis_writer.logical_record.eflr_types import (ChannelItem, ParameterItem, CalibrationMeasurementItem,
                                                   CalibrationCoefficientItem, CalibrationItem, CalibrationSet)


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
