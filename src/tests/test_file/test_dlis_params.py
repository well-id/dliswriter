import pytest
from datetime import datetime
from dlisio import dlis    # type: ignore  # untyped library
from typing import Any, Union
from pytz import utc

from dlis_writer.logical_record.core.eflr.eflr_item import EFLRItem

from tests.common import N_COLS, select_channel


def _check_list(objects: Union[list[EFLRItem], tuple[EFLRItem, ...]], names: Union[list[str], tuple[str, ...]]) -> None:
    """Check that names of the provided objects match the expected names (in the same order)."""

    assert len(objects) == len(names)
    for i, n in enumerate(names):
        assert objects[i].name == n


def test_channel_properties(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of channels in the new DLIS file."""

    for name in ('posix time', 'surface rpm'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [1]
        assert chan.dimension == [1]

    for name in ('amplitude', 'radius', 'radius_pooh'):
        chan = select_channel(short_dlis, name)
        assert chan.name == name
        assert chan.element_limit == [N_COLS]
        assert chan.dimension == [N_COLS]

    assert short_dlis.object("CHANNEL", 'amplitude').units is None
    assert short_dlis.object("CHANNEL", 'radius').units == "in"
    assert short_dlis.object("CHANNEL", 'radius_pooh').units == "m"


def test_channel_not_in_frame(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that channel which was not added to frame is still in the file."""

    name = 'channel_x'
    select_channel(short_dlis, name)  # if no error - channel is found in the file
    assert not any(c.name == name for c in short_dlis.frames[0].channels)


def test_file_header(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of DLIS file header."""

    header = short_dlis.fileheader
    assert header.id == "DEFAULT FHLR"
    assert header.sequencenr == "1"


def test_origin(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Origin in the new DLIS file."""

    assert len(short_dlis.origins) == 1

    origin = short_dlis.origins[0]

    assert origin.name == "DEFAULT ORIGIN"

    # dlisio doesn't add time zone info to the parsed datetime objects, so we use utc.localize here to put it in UTC
    assert (utc.localize(origin.creation_time) ==
            datetime.strptime("2050/03/02 15:30:00", "%Y/%m/%d %H:%M:%S").astimezone(utc))

    assert origin.file_id == "WELL ID"
    assert origin.file_set_name == "Test file set name"
    assert origin.file_set_nr == 1
    assert origin.file_nr == 8
    assert origin.run_nr == [13]
    assert origin.well_id == 5
    assert origin.well_name == "Test well name"
    assert origin.field_name == "Test field name"
    assert origin.company == "Test company"

    # not set - absent from config
    assert origin.producer_name is None
    assert origin.product is None
    assert origin.order_nr is None
    assert origin.version is None
    assert origin.programs == []


def test_frame(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Frame in the new DLIS file."""

    assert len(short_dlis.frames) == 1

    frame = short_dlis.frames[0]

    assert frame.name == "MAIN FRAME"
    assert frame.index_type == "TIME"


def test_storage_unit_label(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Storage Unit Label in the new DLIS file."""

    sul = short_dlis.storage_label()
    assert sul['id'].rstrip(' ') == "DEFAULT STORAGE SET"
    assert sul['sequence'] == 1
    assert sul['maxlen'] == 8192


def test_zones(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of zones in the file matches the expected one."""

    zones = short_dlis.zones
    assert len(zones) == 5


@pytest.mark.parametrize(("name", "description", "maximum", "minimum", "value_type"), (
        ("Zone-1", "BOREHOLE-DEPTH-ZONE", 1300, 100, float),
        ("Zone-2", "VERTICAL-DEPTH-ZONE", 2300.45, 200, float),
        ("Zone-3", "ZONE-TIME", datetime(2050, 7, 13, 11, 30).astimezone(utc),
         datetime(2050, 7, 12, 9).astimezone(utc), datetime),
        ("Zone-4", "ZONE-TIME-2", 90, 10, float),
        ("Zone-X", "Zone not added to any parameter", 10, 1, float)
))
def test_zone_params(short_dlis: dlis.file.LogicalFile, name: str, description: str, maximum: Any,
                     minimum: Any, value_type: type) -> None:
    """Check attributes of zones in the new DLIS file."""

    zones = [zone for zone in short_dlis.zones if zone.name == name]
    assert len(zones) == 1
    z = zones[0]

    assert z.description == description

    assert isinstance(z.maximum, value_type)
    assert isinstance(z.minimum, value_type)

    z_maximum = z.maximum
    z_minimum = z.minimum

    if value_type is datetime:
        # dlisio doesn't add time zone info to the parsed datetime objects; utc.localize marks them as UTC
        z_maximum = utc.localize(z_maximum)  # type: ignore
        z_minimum = utc.localize(z_minimum)  # type: ignore

    assert z_maximum == maximum
    assert z_minimum == minimum


def test_zone_not_in_param(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that a zone which has not been added to any parameter or other object is still in the file."""

    name = 'Zone-X'
    z = [z for z in short_dlis.zones if z.name == name]
    assert len(z) == 1
    for p in short_dlis.parameters:
        z = [z for z in p.zones if z.name == name]
        assert not z


def test_parameters(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of parameters in the DLIS file matches the expected one."""

    params = short_dlis.parameters
    assert len(params) == 3


@pytest.mark.parametrize(("idx", "name", "long_name", "values", "zones"), (
        (0, "Param-1", "LATLONG-GPS", ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"], ["Zone-1", "Zone-3"]),
        (1, "Param-2", "LATLONG", [40.395241, 27.792471], ["Zone-2", "Zone-4"]),
        (2, "Param-3", "SOME-FLOAT-PARAM", [12.5], [])
))
def test_parameters_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, long_name: str, values: list,
                           zones: list[str]) -> None:
    """Check attributes of DLIS Parameter objects."""

    param = short_dlis.parameters[idx]
    assert param.name == name
    assert param.long_name == long_name
    assert param.values.tolist() == values

    _check_list(param.zones, zones)


def test_axes(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of axes in the DLIS file matches the expected one."""

    axes = short_dlis.axes
    assert len(axes) == 2


@pytest.mark.parametrize(("idx", "name", "axis_id", "coordinates"), (
        (0, "Axis-1", "First axis", [40.395241, 27.792471]),
        (1, "Axis-X", "Axis not added to computation", [8])
))
def test_axes_parameters(short_dlis: dlis.file.LogicalFile, idx: int, name: str, axis_id: str,
                         coordinates: list) -> None:
    """Check attributes of axes in the DLIS file."""

    axis = short_dlis.axes[idx]
    assert axis.name == name
    assert axis.axis_id == axis_id
    assert axis.coordinates == coordinates


def test_equipment(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Equipment objects in the DLIS file matches the expected one."""

    eq = short_dlis.equipments
    assert len(eq) == 3


@pytest.mark.parametrize(("idx", "name", "status", "serial_number"), (
        (0, "EQ1", 1, "9101-21391"),
        (1, "EQ2", 0, "5559101-21391"),
        (2, "EqX", 1, "12311")
))
def test_equipment_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, status: int,
                          serial_number: str) -> None:
    eq = short_dlis.equipments[idx]

    assert eq.name == name
    assert eq.status == status
    assert eq.serial_number == serial_number


def test_tool(short_dlis: dlis.file.LogicalFile) -> None:
    tools = short_dlis.tools
    assert len(tools) == 2


@pytest.mark.parametrize(("idx", "name", "description", "status", "param_names", "channel_names"), (
        (0, "TOOL-1", "SOME TOOL", 1, ["Param-1", "Param-3"], ["posix time", "amplitude"]),
        (1, "Tool-X", "desc", 0, ["Param-2"], ["radius_pooh"])
))
def test_tool_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, description: str, status: int,
                     param_names: list[str], channel_names: list[str]) -> None:
    tool = short_dlis.tools[idx]
    assert tool.name == name
    assert tool.description == description
    assert tool.status == status

    _check_list(tool.parameters, param_names)
    _check_list(tool.channels, channel_names)


def test_computation(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Computation objects in the DLIS file matches the expected one."""

    comps = short_dlis.computations
    assert len(comps) == 3


@pytest.mark.parametrize(("idx", "name", "properties", "zone_names", "axis_name", "values"), (
        (0, "COMPT-1", ["PROP 1", "AVERAGED"], ["Zone-1", "Zone-2", "Zone-3"], "Axis-1", [100, 200, 300]),
        (1, "COMPT2", ["PROP 2", "AVERAGED"], ["Zone-1", "Zone-3"], "Axis-1", [1.5, 2.5]),
        (2, "COMPT-X", ["XYZ"], ["Zone-3"], "Axis-1", [12]),
))
def test_computation_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, properties: list[str],
                            zone_names: list[str], axis_name: str, values: list[Union[int, float]]) -> None:
    """Check attributes of Computation objects in the new DLIS file."""

    comp = short_dlis.computations[idx]

    assert comp.name == name
    assert comp.properties == properties
    assert comp.axis[0].name == axis_name
    assert comp.values.tolist() == values

    _check_list(comp.zones, zone_names)


def test_process(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Process objects in the DLIS file matches the expected one."""

    procs = short_dlis.processes
    assert len(procs) == 2


@pytest.mark.parametrize(("idx", "name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        (0, "Process 1", ["radius"], ["amplitude", "Channel 2"], ["COMPT-1"], ["COMPT2"]),
        (1, "Prc2", ["Channel 1"], ["Channel 2"], ["COMPT2", "COMPT-1"], []),
))
def test_process_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, input_channels: list[str],
                        output_channels: list[str], input_compts: list[str], output_compts: list[str]) -> None:
    """Check attributes of Process objects in the new DLIS file."""

    proc = short_dlis.processes[idx]

    assert proc.name == name

    _check_list(proc.input_channels, input_channels)
    _check_list(proc.output_channels, output_channels)
    _check_list(proc.input_computations, input_compts)
    _check_list(proc.output_computations, output_compts)


def test_splices(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Splice objects in the DLIS file matches the expected one."""

    splices = short_dlis.splices
    assert len(splices) == 1


def test_splice_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Test attributes of the Splice object in the new DLIS file."""

    splice = short_dlis.splices[0]

    assert splice.name == "splc1"

    _check_list(splice.zones, ("Zone-1", "Zone-2"))
    _check_list(splice.input_channels, ("Channel 1", "Channel 2"))

    assert splice.output_channel.name == 'amplitude'


def test_calibration_measurement_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of CalibrationMeasurement object in the DLIS file."""

    m = short_dlis.measurements[0]

    assert m.name == "CMEASURE-1"
    assert m.phase == 'BEFORE'
    assert m.axis[0].name == 'Axis-1'
    assert m.source.name == "Channel 1"
    assert m.mtype == 'Plus'
    assert m.samples == [12.2323]
    assert m.samplecount == 12
    assert m.max_deviation == [2.2324]
    assert utc.localize(m.begin_time) == datetime(2050, 3, 12, 12, 30).astimezone(utc)
    assert m.duration == 15
    assert m.reference == [11]
    assert m.standard == [11.2]
    assert m.plus_tolerance == [2]
    assert m.minus_tolerance == [1]


def test_calibration_coefficient_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of CalibrationCoefficient object in the DLIS file."""

    c = short_dlis.coefficients[0]

    assert c.name == "COEF-1"
    assert c.label == 'Gain'
    assert c.coefficients == [100.2, 201.3]
    assert c.references == [89, 298]
    assert c.plus_tolerance == [100.2, 222.124]
    assert c.minus_tolerance == [87.23, 214]


def test_calibration_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Calibration object in the DLIS file."""

    c = short_dlis.calibrations[0]

    assert c.name == 'CALIB-MAIN'

    _check_list(c.calibrated, ("Channel 1", "Channel 2"))
    _check_list(c.uncalibrated, ("amplitude", "radius", "radius_pooh"))
    _check_list(c.coefficients, ("COEF-1",))
    _check_list(c.measurements, ("CMEASURE-1",))
    _check_list(c.parameters, ("Param-1", "Param-2", "Param-3"))


@pytest.mark.parametrize(("idx", "name", "v_zero", "m_decl", "c1_name", "c1_value", "c2_name", "c2_value"), (
        (0, "AQLN WELL-REF", "AQLN vertical_zero", 999.51, "Latitude", 40.395240, "Longitude", 27.792470),
        (1, "WRP-X", "vz20", 112.3, "X", 20, "Y", -0.3)
))
def test_well_reference_point_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, v_zero: str,
                                     m_decl: float, c1_name: str, c1_value: float, c2_name: str,
                                     c2_value: float) -> None:
    """Check attributes of well reference point in the DLIS file."""

    w = short_dlis.wellrefs[idx]

    assert w.name == name
    assert w.vertical_zero == v_zero
    assert w.magnetic_declination == m_decl
    assert w.coordinates[c1_name] == c1_value
    assert w.coordinates[c2_name] == c2_value


def test_message_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attribute of Message object in the DLIS file."""

    m = short_dlis.messages[0]

    assert m.name == "MESSAGE-1"
    assert m.message_type == 'Command'
    assert utc.localize(m.time) == datetime(2050, 3, 4, 11, 23, 11).astimezone(utc)
    assert m.borehole_drift == 123.34
    assert m.vertical_depth == 234.45
    assert m.radial_drift == 345.56
    assert m.angular_drift == 456.67
    assert m.text == ["Test message 11111"]


@pytest.mark.parametrize(("idx", "name", "text"), (
        (0, "COMMENT-1", ["SOME COMMENT HERE"]),
        (1, "cmt2", ["some other comment here", "and another comment"])
))
def test_comment_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, text: str) -> None:
    """Test attributes of Comment objects in the DLIS file."""

    c = short_dlis.comments[idx]

    assert c.name == name
    assert c.text == text


@pytest.mark.parametrize(("idx", "name", "consumer_name", "description"), (
        (0, "no_format_1", "SOME TEXT NOT FORMATTED", "TESTING-NO-FORMAT"),
        (1, "no_fmt2", "xyz", "TESTING NO FORMAT 2")
))
def test_no_format_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, consumer_name: str,
                          description: str) -> None:
    """Check attributes of NoFormat objects in the DLIS file."""

    w = short_dlis.noformats[idx]

    assert w.name == name
    assert w.consumer_name == consumer_name
    assert w.description == description


def test_long_name_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Test attributes of the LongName object in the DLIS file."""

    w = short_dlis.longnames[0]
    t = 'SOME ASCII TEXT'

    assert w.modifier == [t]
    assert w.quantity == t
    assert w.quantity_mod == [t]
    assert w.altered_form == t
    assert w.entity == t
    assert w.entity_mod == [t]
    assert w.entity_nr == t
    assert w.entity_part == t
    assert w.entity_part_nr == t
    assert w.generic_source == t
    assert w.source_part == [t]
    assert w.source_part_nr == [t]
    assert w.conditions == [t]
    assert w.standard_symbol == t
    assert w.private_symbol == t


@pytest.mark.parametrize(("idx", "name", "description", "object_type", "object_names", "group_names"), (
        (0, "ChannelGroup", "Group of channels", "CHANNEL", ["Channel 1", "Channel 2"], []),
        (1, "ProcessGroup", "Group of processes", "PROCESS", ["Process 1", "Prc2"], []),
        (2, "MultiGroup", "Group of groups", "GROUP", [], ["ChannelGroup", "ProcessGroup"])
))
def test_group_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, description: str, object_type: str,
                      object_names: list[str], group_names: list[str]) -> None:
    """Test attributes of Group objects in the DLIS file."""

    g = short_dlis.groups[idx]
    assert g.name == name
    assert g.description == description
    assert g.objecttype == object_type
    _check_list(g.objects, object_names)
    _check_list(g.groups, group_names)
