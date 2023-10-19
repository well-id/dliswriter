import os
import pytest
from datetime import datetime

from dlis_writer.tests.common import base_data_path, config_params
from dlis_writer.tests.test_writer.common import reference_data, short_reference_data
from dlis_writer.tests.test_writer.common import N_COLS, load_dlis, select_channel, write_dlis_file


@pytest.fixture(scope='session')
def short_dlis(short_reference_data, base_data_path, config_params):
    dlis_path = base_data_path/'outputs/new_fake_dlis_shared.DLIS'

    channel_names = [f"Channel-{s}" for s in ("time", "rpm", "amplitude", "radius", "radius_pooh")]
    config_params['Frame']['channels'] = ', '.join(channel_names)

    write_dlis_file(data=short_reference_data, dlis_file_name=dlis_path, config=config_params)

    with load_dlis(dlis_path) as f:
        yield f

    if dlis_path.exists():  # does not exist if file creation failed
        os.remove(dlis_path)


def _check_list(objects, names):
    assert len(objects) == len(names)
    for i, n in enumerate(names):
        assert objects[i].name == n


def test_channel_properties(short_dlis, config_params):
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
    assert short_dlis.object("CHANNEL", 'radius').units == "inch"
    assert short_dlis.object("CHANNEL", 'radius_pooh').units == "meter"


def test_channel_not_in_frame(short_dlis, config_params):
    name = 'channel_x'
    chan = select_channel(short_dlis, name)
    assert name not in config_params['Frame']['channels']


def test_file_header(short_dlis, config_params):
    header = short_dlis.fileheader
    assert header.id == config_params['FileHeader']['name']
    assert header.sequencenr == config_params['FileHeader']['sequence_number']


def test_origin(short_dlis, config_params):
    assert len(short_dlis.origins) == 1

    origin = short_dlis.origins[0]
    conf = config_params['Origin']

    assert origin.name == conf['name']
    assert origin.creation_time == datetime.strptime(conf['creation_time'], "%Y/%m/%d %H:%M:%S")
    assert origin.file_id == conf['file_id']
    assert origin.file_set_name == conf['file_set_name']
    assert origin.file_set_nr == int(conf['file_set_number'])
    assert origin.file_nr == int(conf['file_number'])
    assert origin.run_nr == [int(conf['run_number'])]
    assert origin.well_id == int(conf['well_id'])
    assert origin.well_name == conf['well_name']
    assert origin.field_name == conf['field_name']
    assert origin.company == conf['company']

    # not set - absent from config
    assert origin.producer_name is None
    assert origin.product is None
    assert origin.order_nr is None
    assert origin.version is None
    assert origin.programs == []


def test_frame(short_dlis, config_params):
    assert len(short_dlis.frames) == 1

    frame = short_dlis.frames[0]

    assert frame.name == config_params['Frame']['name']
    assert frame.index_type == config_params['Frame']['index_type']


def test_storage_unit_label(short_dlis, config_params):
    sul = short_dlis.storage_label()
    assert sul['id'].rstrip(' ') == config_params['StorageUnitLabel']['name']
    assert sul['sequence'] == int(config_params['StorageUnitLabel']['sequence_number'])
    assert sul['maxlen'] == 8192


def test_zones(short_dlis):
    zones = short_dlis.zones
    assert len(zones) == 5


@pytest.mark.parametrize(("idx", "name", "description", "maximum", "minimum", "value_type"), (
        (0, "Zone-1", "BOREHOLE-DEPTH-ZONE", 1300, 100, int),
        (1, "Zone-2", "VERTICAL-DEPTH-ZONE", 2300.45, 200, float),
        (2, "Zone-3", "ZONE-TIME", datetime(2050, 7, 13, 11, 30), datetime(2050, 7, 12, 9), datetime),
        (3, "Zone-4", "ZONE-TIME-2", 90, 10, int),
        (4, "Zone-X", "Zone not added to any parameter", 10, 1, int)
))
def test_zone_params(short_dlis, idx, name, description, maximum, minimum, value_type):
    z = short_dlis.zones[idx]
    assert z.name == name
    assert z.description == description

    assert z.maximum == maximum
    assert z.minimum == minimum
    assert isinstance(z.maximum, value_type)
    assert isinstance(z.minimum, value_type)


def test_zone_not_in_param(short_dlis):
    name = 'Zone-X'
    z = [z for z in short_dlis.zones if z.name == name]
    assert len(z) == 1
    for p in short_dlis.parameters:
        z = [z for z in p.zones if z.name == name]
        assert not z


def test_parameters(short_dlis):
    params = short_dlis.parameters
    assert len(params) == 3


@pytest.mark.parametrize(("idx", "name", "long_name", "values", "zones"), (
        (0, "Param-1", "LATLONG-GPS", ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"], ["Zone-1", "Zone-3"]),
        (1, "Param-2", "LATLONG", [40.395241, 27.792471], ["Zone-2", "Zone-4"]),
        (2, "Param-3", "SOME-FLOAT-PARAM", [12.5], [])
))
def test_parameters_params(short_dlis, idx, name, long_name, values, zones):
    param = short_dlis.parameters[idx]
    assert param.name == name
    assert param.long_name == long_name
    assert param.values.tolist() == values

    _check_list(param.zones, zones)


def test_axes(short_dlis):
    axes = short_dlis.axes
    assert len(axes) == 2


@pytest.mark.parametrize(("idx", "name", "axis_id", "coordinates"), (
        (0, "Axis-1", "First axis", [40.395241, 27.792471]),
        (1, "Axis-X", "Axis not added to computation", [8])
))
def test_axes_parameters(short_dlis, idx, name, axis_id, coordinates):
    axis = short_dlis.axes[idx]
    assert axis.name == name
    assert axis.axis_id == axis_id
    assert axis.coordinates == coordinates


def test_equipment(short_dlis):
    eq = short_dlis.equipments
    assert len(eq) == 3


@pytest.mark.parametrize(("idx", "name", "status", "serial_number"), (
        (0, "EQ1", 1, "9101-21391"),
        (1, "EQ2", None, "5559101-21391"),
        (2, "EqX", 1, "12311")
))
def test_equipment_params(short_dlis, idx, name, status, serial_number):
    eq = short_dlis.equipments[idx]

    assert eq.name == name
    assert eq.status == status
    assert eq.serial_number == serial_number


def test_tool(short_dlis):
    tools = short_dlis.tools
    assert len(tools) == 2


@pytest.mark.parametrize(("idx", "name", "description", "status", "param_names", "channel_names"), (
        (0, "TOOL-1", "SOME TOOL", 1, ["Param-1", "Param-3"], ["posix time", "amplitude"]),
        (1, "Tool-X", "desc", None, ["Param-2"], ["radius_pooh"])
))
def test_tool_params(short_dlis, idx, name, description, status, param_names, channel_names):
    tool = short_dlis.tools[idx]
    assert tool.name == name
    assert tool.description == description
    assert tool.status == status

    _check_list(tool.parameters, param_names)
    _check_list(tool.channels, channel_names)


def test_computation(short_dlis):
    comps = short_dlis.computations
    assert len(comps) == 3


@pytest.mark.parametrize(("idx", "name", "properties", "zone_names", "axis_name", "values"), (
        (0, "COMPT-1", ["PROP 1", "AVERAGED"], ["Zone-1", "Zone-2", "Zone-3"], "Axis-1", [100, 200, 300]),
        (1, "COMPT2", ["PROP 2", "AVERAGED"], ["Zone-1", "Zone-3"], "Axis-1", [1.5, 2.5, 3]),
        (2, "COMPT-X", ["XYZ"], ["Zone-3"], "Axis-1", [12]),
))
def test_computation_params(short_dlis, idx, name, properties, zone_names, axis_name, values):
    comp = short_dlis.computations[idx]

    assert comp.name == name
    assert comp.properties == properties
    assert comp.axis[0].name == axis_name
    assert comp.values.tolist() == values

    _check_list(comp.zones, zone_names)


def test_process(short_dlis):
    procs = short_dlis.processes
    assert len(procs) == 2


@pytest.mark.parametrize(("idx", "name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        (0, "Process 1", ["radius"], ["amplitude", "Channel 2"], ["COMPT-1"], ["COMPT2"]),
        (1, "Prc2", ["Channel 1"], ["Channel 2"], ["COMPT2", "COMPT-1"], []),
))
def test_process_params(short_dlis, idx, name, input_channels, output_channels, input_compts, output_compts):
    proc = short_dlis.processes[idx]

    assert proc.name == name

    _check_list(proc.input_channels, input_channels)
    _check_list(proc.output_channels, output_channels)
    _check_list(proc.input_computations, input_compts)
    _check_list(proc.output_computations, output_compts)


def test_splices(short_dlis):
    splices = short_dlis.splices
    assert len(splices) == 1


def test_splice_params(short_dlis):
    splice = short_dlis.splices[0]

    assert splice.name == "splc1"

    _check_list(splice.zones, ("Zone-1", "Zone-2"))
    _check_list(splice.input_channels, ("Channel 1", "Channel 2"))

    assert splice.output_channel.name == 'amplitude'


def test_calibration_measurement_params(short_dlis):
    m = short_dlis.measurements[0]

    assert m.name == "CMEASURE-1"
    assert m.phase == 'BEFORE'
    assert m.axis[0].name == 'Axis-1'
    assert m.source.name == "Channel 1"
    assert m.mtype == 'Plus'
    assert m.samples == [12.2323]
    assert m.samplecount == 12
    assert m.max_deviation == [2.2324]
    assert m.begin_time == datetime(2050, 3, 12, 12, 30)
    assert m.duration == 15
    assert m.reference == [11]
    assert m.standard == [11.2]
    assert m.plus_tolerance == [2]
    assert m.minus_tolerance == [1]


def test_calibration_coefficient_params(short_dlis):
    c = short_dlis.coefficients[0]

    assert c.name == "COEF-1"
    assert c.label == 'Gain'
    assert c.coefficients == [100.2, 201.3]
    assert c.references == [89, 298]
    assert c.plus_tolerance == [100.2, 222.124]
    assert c.minus_tolerance == [87.23, 214]


def test_calibration_params(short_dlis):
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
def test_well_reference_point_params(short_dlis, idx, name, v_zero, m_decl, c1_name, c1_value, c2_name, c2_value):
    w = short_dlis.wellrefs[idx]

    assert w.name == name
    assert w.vertical_zero == v_zero
    assert w.magnetic_declination == m_decl
    assert w.coordinates[c1_name] == c1_value
    assert w.coordinates[c2_name] == c2_value


@pytest.mark.parametrize(("idx", "name", "channels", "depth", "radial_drift", "angular_drift", "time"), (
        (0, "PATH1", ("Channel 1", "Channel 2"), -187, 105, 64.23, 180),
        (1, "path2", ("amplitude",), 120, 3, -12.3, 4)
))
def test_path_params(short_dlis, idx, name, channels, depth, radial_drift, angular_drift, time):
    p = short_dlis.paths[idx]

    assert p.name == name
    assert p.frame.name == 'MAIN FRAME'
    assert p.well_reference_point.name == 'AQLN WELL-REF'

    assert len(p.value) == len(channels)
    for i, c in enumerate(channels):
        assert p.value[i].name == c

    assert p.vertical_depth == depth
    assert p.radial_drift == radial_drift
    assert p.angular_drift == angular_drift
    assert p.time == time
