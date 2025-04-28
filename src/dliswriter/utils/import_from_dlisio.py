from dliswriter import DLISFile, LogicalFile, enums, eflr_types, StorageUnitLabel
from dliswriter.file.eflr_sets_dict import AnyEFLRSet, AnyEFLRItem
from dliswriter.logical_record.core.eflr import EFLRSet
from typing import Union, Dict, Generic, Optional
try:
    import dlisio    # type: ignore  # untyped library
except ImportError:
    raise ImportError(
        "The 'dlisio' library is required to use this function. "
        "You can install dlisio or reinstall dliswriter calling 'pip install dliswriter[dlisio]'"
    )
from dlisio.dlis.utils.valuetypes import scalar, parsevalue    # type: ignore  # untyped library

import logging

logger = logging.getLogger(__name__)


# dliswriter EFLRSets corresponding to dlisio types
class DlisioObjectToDliswriterSet(Generic[AnyEFLRSet]):
    def __init__(self) -> None:
        self.data: Dict[dlisio.dlis.BasicObject, type[EFLRSet]] = {}

    def fill_entries(self) -> None:
        self.data[dlisio.dlis.computation.Computation] = eflr_types.ComputationSet
        self.data[dlisio.dlis.axis.Axis] = eflr_types.AxisSet
        self.data[dlisio.dlis.coefficient.Coefficient] = eflr_types.CalibrationCoefficientSet
        self.data[dlisio.dlis.calibration.Calibration] = eflr_types.CalibrationSet
        self.data[dlisio.dlis.measurement.Measurement] = eflr_types.CalibrationMeasurementSet
        self.data[dlisio.dlis.channel.Channel] = eflr_types.ChannelSet
        self.data[dlisio.dlis.comment.Comment] = eflr_types.CommentSet
        self.data[dlisio.dlis.equipment.Equipment] = eflr_types.EquipmentSet
        self.data[dlisio.dlis.fileheader.Fileheader] = eflr_types.FileHeaderSet
        self.data[dlisio.dlis.frame.Frame] = eflr_types.FrameSet
        self.data[dlisio.dlis.group.Group] = eflr_types.GroupSet
        self.data[dlisio.dlis.longname.Longname] = eflr_types.LongNameSet
        self.data[dlisio.dlis.message.Message] = eflr_types.MessageSet
        self.data[dlisio.dlis.noformat.Noformat] = eflr_types.NoFormatSet
        self.data[dlisio.dlis.origin.Origin] = eflr_types.OriginSet
        self.data[dlisio.dlis.parameter.Parameter] = eflr_types.ParameterSet
        self.data[dlisio.dlis.path.Path] = eflr_types.PathSet
        self.data[dlisio.dlis.process.Process] = eflr_types.ProcessSet
        self.data[dlisio.dlis.splice.Splice] = eflr_types.SpliceSet
        self.data[dlisio.dlis.tool.Tool] = eflr_types.ToolSet
        self.data[dlisio.dlis.wellref.Wellref] = eflr_types.WellReferencePointSet
        self.data[dlisio.dlis.zone.Zone] = eflr_types.ZoneSet


dlisio_to_dliswriter: DlisioObjectToDliswriterSet = DlisioObjectToDliswriterSet()
dlisio_to_dliswriter.fill_entries()


def dliswriter_Set(dlisio_type: type[dlisio.dlis.BasicObject]) -> type[EFLRSet]:
    """
    Output the dliswriter EFLRSet type corresponding to the dlisio_type
    """
    assert dlisio_type in dlisio_to_dliswriter.data, \
        f"Error converting dlisio data to dliswriter. Are you sure there exists a type {dlisio_type} in dlisio?"
    return dlisio_to_dliswriter.data[dlisio_type]


def is_same_object(obj_dliswriter: AnyEFLRItem, obj_dlisio: dlisio.dlis.BasicObject) -> bool:
    """
    Compare if an object in dlisio and another in dliswriter representation are the same.
    NOTE - Only the attributes that make a general object unique inside a logical file are compared,
    while the remainging attributes are not checked
    """
    # NOTE: dlisio is untyped. Types were casted according to current dlisio implementation
    return (obj_dliswriter.name == str(obj_dlisio.name)) and \
        (obj_dliswriter.origin_reference == int(obj_dlisio.origin)) and \
        (obj_dliswriter.copy_number == int(obj_dlisio.copynumber))


def find_in_dliswriter(logical_file: LogicalFile, object_from_dlisio: dlisio.dlis.BasicObject) \
   -> Union[AnyEFLRItem, None]:  # Union[AnyEFLRItem, None]:
    """
    Find the dliswriter object in the logical file that is equivalent to object_from_dlisio
    """
    if not object_from_dlisio:
        return None

    ref = None
    candidates: Optional[list[AnyEFLRItem]] = \
        list(logical_file._eflr_sets.get_all_items_for_set_type(dliswriter_Set(type(object_from_dlisio))))
    if candidates:
        for c in candidates:
            if is_same_object(c, object_from_dlisio):
                ref = c
                break  # NOTE - We return here, as it shouldn't be possible to have more than one match

    if not ref:
        raise RuntimeError(
            f"Couldn't find in dliswriter logical file the reference of dlisio's object {object_from_dlisio}.")

    return ref


def find_dlisio_objects_in_dliswriter(
    dlisio_objs: list[dlisio.dlis.BasicObject], dliswriter_candidates: list[AnyEFLRItem]) \
     -> Union[list[AnyEFLRItem], None]:
    """
    Find the list of objects in dliswriter_candidates that matches the list of objects dlisio_objs
    """
    if not dlisio_objs or not len(dlisio_objs):
        return None

    objs: list[AnyEFLRItem] = []
    for dlisw in dliswriter_candidates:
        for o in dlisio_objs:
            if is_same_object(dlisw, o):
                objs.append(dlisw)

    if len(objs) != len(dlisio_objs):
        msg = f"Couldn't find in dliswriter logical file some or all {type(dliswriter_candidates[0])} references "
        f"listed in list of dlisio objects {dlisio_objs}"
        raise RuntimeError(msg)

    return objs


def convert_dlisio_to_int(dlisio_in: Union[int, str, None]) -> Union[int, None]:
    out_nr = None
    if dlisio_in:
        if type(dlisio_in) is not int:
            out_nr = (
                int(parsevalue(dlisio_in, scalar))
                if len(str(dlisio_in)) != 0  # typecasting to pass mypy, even though str is guaranteed from checks above
                else None
            )
        else:
            out_nr = dlisio_in

    return out_nr


def add_origins(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for idx_o, o in enumerate(dlisio_lf.origins):
        programs = o["PROGRAMS"] if len(o["PROGRAMS"]) != 0 else None

        # NOTE - dliswriter expects int, dlisio a list. rp66v1 doesn't specify
        run_nr = convert_dlisio_to_int(o["RUN-NUMBER"])

        # NOTE - dliswriter expects int, dlisio a list. rp66v1 doesn't specify
        descent_nr = convert_dlisio_to_int(o["DESCENT-NUMBER"])

        out_logical_file.add_origin(
            name=o.name,
            origin_reference=o.origin,
            file_set_number=o["FILE-SET-NUMBER"],
            file_set_name=o["FILE-SET-NAME"],
            file_number=o["FILE-NUMBER"],
            file_type=o["FILE-TYPE"],
            product=o["PRODUCT"],
            version=o["VERSION"],
            programs=programs,
            order_number=o["ORDER-NUMBER"],
            descent_number=descent_nr,
            run_number=run_nr,
            well_id=o["WELL-ID"],
            well_name=o["WELL-NAME"],
            field_name=o["FIELD-NAME"],
            producer_code=o["PRODUCER-CODE"],
            producer_name=o["PRODUCER-NAME"],
            company=o["COMPANY"],
            name_space_name=o["NAME-SPACE-NAME"],
            name_space_version=o["NAME-SPACE-VERSION"],
            set_name=f"ORIGIN-LF{lf_index}",
        )


def add_axes(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for a in dlisio_lf.axes:
        out_logical_file.add_axis(
            name=a.name,
            axis_id=a.axis_id,
            coordinates=a.coordinates,
            # spacing=a.spacing,  NOTE - not always dlisio will return a number - rp66v1 doesn't specify a type
            set_name=f"AXES-LF{lf_index}",
            origin_reference=a.origin
        )


def add_equipments(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for e in dlisio_lf.equipments:
        out_logical_file.add_equipment(
            name=e.name,
            trademark_name=e.trademark_name,
            status=e.status,
            eq_type=e.generic_type,
            serial_number=e.serial_number,
            location=e.location,
            height=e.height,
            length=e.length,
            minimum_diameter=e.diameter_min,
            maximum_diameter=e.diameter_max,
            volume=e.volume,
            weight=e.weight,
            hole_size=e.hole_size,
            pressure=e.pressure,
            temperature=e.temperature,
            vertical_depth=e.vertical_depth,
            radial_drift=e.radial_drift,
            angular_drift=e.angular_drift,
            set_name=f"EQUIPMENTS-LF{lf_index}",
            origin_reference=e.origin,
        )


def add_wellrefs(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for r in dlisio_lf.wellrefs:
        out_logical_file.add_well_reference_point(
            name=r.name,
            permanent_datum=r.permanent_datum,
            vertical_zero=r.vertical_zero,
            permanent_datum_elevation=r.permanent_datum_elevation,
            above_permanent_datum=r.above_permanent_datum,
            magnetic_declination=r.magnetic_declination,
            coordinate_1_name=r['COORDINATE-1-NAME'],
            coordinate_1_value=r['COORDINATE-1-VALUE'],
            coordinate_2_name=r['COORDINATE-2-NAME'],
            coordinate_2_value=r['COORDINATE-2-VALUE'],
            coordinate_3_name=r['COORDINATE-3-NAME'],
            coordinate_3_value=r['COORDINATE-3-VALUE'],
            set_name=f"WELLREFS-LF{lf_index}",
            origin_reference=r.origin,
        )


def add_zones(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for z in dlisio_lf.zones:
        out_logical_file.add_zone(
            name=z.name,
            description=z.description,
            domain=z.domain,
            maximum=z.maximum,
            minimum=z.minimum,
            set_name=f"ZONES-LF{lf_index}",
            origin_reference=z.origin,
        )


def add_longnames(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for ln in dlisio_lf.longnames:
        out_logical_file.add_long_name(
            name=ln.name,
            general_modifier=ln.modifier,
            quantity=ln.quantity,
            quantity_modifier=ln.quantity_mod,
            altered_form=ln.altered_form,
            entity=ln.entity,
            entity_modifier=ln.entity_mod,
            entity_number=ln.entity_nr,
            entity_part=ln.entity_part,
            entity_part_number=ln.entity_part_nr,
            generic_source=ln.generic_source,
            source_part=ln.source_part,
            source_part_number=ln.source_part_nr,
            conditions=ln.conditions,
            standard_symbol=ln.standard_symbol,
            private_symbol=ln.private_symbol,
            set_name=f"LONGNAMES-LF{lf_index}",
            origin_reference=ln.origin,
        )


def add_calibration_coefficients(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile,
                                 lf_index: int) -> None:
    for c in dlisio_lf.coefficients:
        coeffs = c.coefficients if len(c.coefficients) else None
        refs = c.references if len(c.references) else None
        plus = c.plus_tolerance if len(c.plus_tolerance) else None
        minus = c.minus_tolerance if len(c.minus_tolerance) else None
        out_logical_file.add_calibration_coefficient(
            name=c.name,
            label=c.label,
            coefficients=coeffs,
            references=refs,
            plus_tolerances=plus,
            minus_tolerances=minus,
            set_name=f"COEFFICIENTS-LF{lf_index}",
            origin_reference=c.origin,
        )


def find_longname(out_logical_file: LogicalFile, dlisio_longname: Union[dlisio.dlis.Longname, str]) \
   -> Optional[Union[eflr_types.LongNameItem, str]]:
    lname = None
    if (dlisio_longname):
        if type(dlisio_longname) is str:
            lname = dlisio_longname
        elif dlisio_longname is not None:
            lname = find_in_dliswriter(out_logical_file, dlisio_longname)

    return lname


def add_channels_and_frames(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_axes: list[eflr_types.AxisItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.AxisSet))
    for f, frame in enumerate(dlisio_lf.frames):

        channels = []

        for c, channel in enumerate(frame.channels):

            properties = channel.properties if len(channel.properties) != 0 else None

            # finding references of axes
            # NOTE - in dlisio the Channel has an axeS attribute (a list)!
            # Since dliswriter channel takes a single axis (is it correct?), we'll use the the first element
            axis: Optional[eflr_types.AxisItem] = None
            axes: Optional[list[eflr_types.AxisItem]] = find_dlisio_objects_in_dliswriter(channel.axis, out_axes)
            if axes:
                if len(axes):
                    axis = axes[0]

            # finding reference of longname
            lname = find_longname(out_logical_file, channel.long_name)

            units = None
            if (channel.units):
                if type(channel.units) is not str:
                    units = channel.units.decode("latin1")  # Normally a good guess. Degree symbol, for example
                else:
                    units = channel.units

            # minimum_value, maximum_value and source should be automatically set internally
            # NOTE - frame.curves() would be faster than channel-wise retrieveing channel.curves()
            # (https://dlisio.readthedocs.io/en/latest/dlis/api.html#dlisio.dlis.Channel.curves)
            channels.append(
                out_logical_file.add_channel(
                    name=channel.name,
                    # dataset_name: Optional[str] = None,  not in the rp66v1 specification, nor in dlisio
                    data=channel.curves(),
                    cast_dtype=channel.dtype.base,
                    long_name=lname,
                    dimension=channel.dimension,
                    element_limit=channel.element_limit,
                    properties=properties,
                    axis=axis,
                    units=units,
                    set_name=f"CHANNELS-LF{lf_index}-F{f}",
                    origin_reference=frame.origin,
                )
            )

        if len(channels) == 0:  # dliswriter doesn't allow frames without channels
            continue

        index_type = frame.index_type
        if frame.index_type not in [enums.FrameIndexType.ANGULAR_DRIFT, enums.FrameIndexType.BOREHOLE_DEPTH,
                                    enums.FrameIndexType.NON_STANDARD, enums.FrameIndexType.RADIAL_DRIFT,
                                    enums.FrameIndexType.VERTICAL_DEPTH]:
            logger.warning(f"Frame index_type of Frame {frame.name} doesn't belong to the rp66v1 allowed values. "
                           f"Potentially unsafe.")

        out_logical_file.add_frame(
            name=frame.name,
            channels=channels,
            description=frame.description,
            encrypted=int(frame.encrypted),
            set_name=f"FRAMES-LF{lf_index}",
            origin_reference=frame.origin,
            index_type=index_type,
        )


def add_parameters(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_axes: list[eflr_types.AxisItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.AxisSet))
    out_zones: list[eflr_types.ZoneItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ZoneSet))

    for p in dlisio_lf.parameters:
        axes_refs = find_dlisio_objects_in_dliswriter(p.axis, out_axes)
        zones_refs = find_dlisio_objects_in_dliswriter(p.zones, out_zones)

        # finding reference of longname
        lname = find_longname(out_logical_file, p.long_name)

        out_logical_file.add_parameter(
            name=p.name,
            long_name=lname,
            # dimension=p.dimension,  NOTE - Check: Some tests lead to to errors at dliswriter checks
            values=p.values.tolist(),
            # FIXME - rp66v1 4.4.4: 'The AXIS Attribute is a List of references to one or more Axis Objects'
            # But dliswriter expects a single AxisItem. We'll use the first one from dlisio
            axis=axes_refs[0] if axes_refs else None,
            zones=zones_refs,
            set_name=f"PARAMETERS-LF{lf_index}",
            origin_reference=p.origin,
        )


def add_calibrations(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_channels: list[eflr_types.ChannelItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))
    out_coefficients: list[eflr_types.CalibrationCoefficientItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.CalibrationCoefficientSet))
    out_measurements: list[eflr_types.CalibrationMeasurementItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.CalibrationMeasurementSet))
    out_parameters: list[eflr_types.ParameterItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ParameterSet))

    for c in dlisio_lf.calibrations:
        cal_channels_refs = find_dlisio_objects_in_dliswriter(c.calibrated, out_channels)
        uncal_channels_refs = find_dlisio_objects_in_dliswriter(c.uncalibrated, out_channels)
        coeffs_refs = find_dlisio_objects_in_dliswriter(c.coefficients, out_coefficients)
        measurements_refs = find_dlisio_objects_in_dliswriter(c.measurements, out_measurements)
        parameters_refs = find_dlisio_objects_in_dliswriter(c.parameters, out_parameters)

        out_logical_file.add_calibration(
            name=c.name,
            calibrated_channels=cal_channels_refs,
            uncalibrated_channels=uncal_channels_refs,
            coefficients=coeffs_refs,
            measurements=measurements_refs,
            parameters=parameters_refs,
            method=c.method,
            set_name=f"PARAMETERS-LF{lf_index}",
            origin_reference=c.origin
        )


def add_measurements(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_axes: list[eflr_types.AxisItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.AxisSet))

    for m in dlisio_lf.measurements:
        phase = m.phase
        if m.phase not in [enums.CalibrationMeasurementPhase.BEFORE, enums.CalibrationMeasurementPhase.AFTER,
           enums.CalibrationMeasurementPhase.MASTER]:
            logger.warning(f"Measurement {m.name} - phase should be 'AFTER', 'BEFORE' or 'MASTER'. Potentially unsafe.")

        # finding references of axes
        # NOTE - in dlisio the Measurement has an axis attribute that is a list!
        # Since dliswriter calibration_measurement has a single axis (is it correct?), we'll use the the first element
        axis = None
        axes = find_dlisio_objects_in_dliswriter(m.axis, out_axes)
        if axes:
            if len(axes):
                axis = axes[0]

        out_logical_file.add_calibration_measurement(
            name=m.name,
            phase=phase,
            measurement_type=m.mtype,
            dimension=m.dimension,
            axis=axis,
            measurement=m["MEASUREMENT"],
            sample_count=m.samplecount,
            maximum_deviation=m.max_deviation.tolist(),
            standard_deviation=m.std_deviation.tolist(),
            begin_time=m.begin_time,
            duration=m.duration,
            reference=m.reference.tolist(),
            standard=m.standard,
            plus_tolerance=m.plus_tolerance.tolist(),
            minus_tolerance=m.minus_tolerance.tolist(),
            set_name=f"MESSAGES-LF{lf_index}",
            origin_reference=m.origin,
        )


def add_comments(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for c in dlisio_lf.comments:
        out_logical_file.add_comment(
            name=c.name,
            text=c.text,
            set_name=f"COMMENTS-LF{lf_index}",
            origin_reference=c.origin,
        )


def add_processes(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_channels: list[eflr_types.ChannelItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))
    out_parameters: list[eflr_types.ParameterItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ParameterSet))

    for p in dlisio_lf.processes:
        input_channels_refs = find_dlisio_objects_in_dliswriter(p.input_channels, out_channels)
        output_channels_refs = find_dlisio_objects_in_dliswriter(p.output_channels, out_channels)
        parameters_refs = find_dlisio_objects_in_dliswriter(p.parameters, out_parameters)

        out_logical_file.add_process(
            name=p.name,
            description=p.description,
            trademark_name=p.trademark_name,
            version=p.version,
            properties=p.properties,
            status=p.status,
            input_channels=input_channels_refs,
            output_channels=output_channels_refs,
            parameters=parameters_refs,
            comments=p.comments,
            set_name=f"PARAMETERS-LF{lf_index}",
            origin_reference=p.origin,
        )


def add_computations(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_axes: list[eflr_types.AxisItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.AxisSet))
    out_zones: list[eflr_types.ZoneItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ZoneSet))

    for c in dlisio_lf.computations:
        lname = find_longname(out_logical_file, c.long_name)

        axes_refs = find_dlisio_objects_in_dliswriter(c.axis, out_axes)
        zones_refs = find_dlisio_objects_in_dliswriter(c.zones, out_zones)

        # dim = c.dimension if c.dimension else None

        out_logical_file.add_computation(
            name=c.name,
            long_name=lname,
            properties=c.properties,
            # dimension=dim,
            axis=axes_refs,
            zones=zones_refs,
            values=c.values.tolist(),
            set_name=f"COMPUTATION-LF{lf_index}",
            origin_reference=c.origin,
        )


def objectListInGroup(dlisio_group: dlisio.dlis.Group, out_logical_file: LogicalFile) \
   -> Union[list[AnyEFLRItem], None]:
    olist: Optional[list[AnyEFLRItem]] = []
    for o in dlisio_group.objects:
        ref: Optional[AnyEFLRItem] = find_in_dliswriter(out_logical_file, o)
        if ref:
            olist.append(ref)  # type: ignore  # we're inside if(ref)
    if not len(olist):  # type: ignore  # at this point olist can't be None
        return None
    return olist


def add_groups(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for g in dlisio_lf.groups:
        out_logical_file.add_group(
            name=g.name,
            description=g.description,
            object_list=objectListInGroup(g, out_logical_file),
            set_name=f"GROUPS-LF{lf_index}",
            origin_reference=g.origin,
        )

    out_groups: list[eflr_types.GroupItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.GroupSet))

    for idx_g, group in enumerate(out_groups):
        group_list = []
        for g in dlisio_lf.groups:
            if (group.name == g.name):
                group_list.append(group)
        if len(group_list) > 0:
            group.group_list.value = group_list


def add_messages(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for m in dlisio_lf.messages:
        out_logical_file.add_message(
            name=m.name,
            message_type=m.message_type,
            time=m.time,                        # NOTE - m.time is crtime. time is dtime_or_number_type
            borehole_drift=m.borehole_drift,
            vertical_depth=m.vertical_depth,
            radial_drift=m.radial_drift,
            angular_drift=m.angular_drift,
            text=m.text,
            set_name=f"MESSAGES-LF{lf_index}",
            origin_reference=m.origin,
        )


def add_paths(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_channels: list[eflr_types.ChannelItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))

    for p in dlisio_lf.paths:
        well_rp_ref: Optional[eflr_types.WellReferencePointItem] = \
            find_in_dliswriter(out_logical_file, p.well_reference_point)
        frame_ref: Optional[eflr_types.FrameItem] = find_in_dliswriter(out_logical_file, p.frame)

        channel_refs = find_dlisio_objects_in_dliswriter(p.value, out_channels)
        borehole_depth_ref = find_in_dliswriter(out_logical_file, p.borehole_depth)
        vertical_depth_ref = find_in_dliswriter(out_logical_file, p.vertical_depth)
        radial_drift_ref = find_in_dliswriter(out_logical_file, p.radial_drift)
        angular_drift_ref = find_in_dliswriter(out_logical_file, p.angular_drift)

        # From file.py's add_frame: 'This Attribute should not be present if the Frame Type
        # for the current Path has an Index-Type Value of TIME.'
        time_ref = None
        if (frame_ref and frame_ref.index_type != "TIME"):
            time_ref = find_in_dliswriter(out_logical_file, p.time)

        out_logical_file.add_path(
            name=p.name,
            frame_type=frame_ref,
            well_reference_point=well_rp_ref,
            value=channel_refs,
            borehole_depth=borehole_depth_ref,
            vertical_depth=vertical_depth_ref,
            radial_drift=radial_drift_ref,
            angular_drift=angular_drift_ref,
            time=time_ref,
            depth_offset=p.depth_offset,
            measure_point_offset=p.measure_point_offset,
            tool_zero_offset=p.tool_zero_offset,
            set_name=f"PATHS-LF{lf_index}",
            origin_reference=p.origin,
        )


def add_splices(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_channels: list[eflr_types.ChannelItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))
    out_zones: list[eflr_types.ZoneItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ZoneSet))

    for s in dlisio_lf.splices:
        output_channel_ref = find_in_dliswriter(out_logical_file, s.output_channel)
        input_channels_refs = find_dlisio_objects_in_dliswriter(s.input_channels, out_channels)
        zones_refs = find_dlisio_objects_in_dliswriter(s.zones, out_zones)

        out_logical_file.add_splice(
            name=s.name,
            output_channel=output_channel_ref,
            input_channels=input_channels_refs,
            zones=zones_refs,
            set_name=f"SPLICES-LF{lf_index}",
            origin_reference=s.origin,
        )


def add_tools(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    out_channels: list[eflr_types.ChannelItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))
    out_parameters: list[eflr_types.ParameterItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ParameterSet))
    out_equipments: list[eflr_types.EquipmentItem] = \
        list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.EquipmentSet))

    for t in dlisio_lf.tools:
        output_channels_refs = find_dlisio_objects_in_dliswriter(t.channels, out_channels)
        out_parameters_refs = find_dlisio_objects_in_dliswriter(t.parameters, out_parameters)
        equipments_refs = find_dlisio_objects_in_dliswriter(t.parts, out_equipments)

        out_logical_file.add_tool(
            name=t.name,
            trademark_name=t.trademark_name,
            generic_name=t.generic_name,
            parts=equipments_refs,
            status=t.status,
            channels=output_channels_refs,
            parameters=out_parameters_refs,
            set_name=f"TOOLS-LF{lf_index}",
            origin_reference=t.origin,
        )


def add_noformats(dlisio_lf: dlisio.dlis.LogicalFile, out_logical_file: LogicalFile, lf_index: int) -> None:
    for n in dlisio_lf.noformats:
        out_logical_file.add_no_format(
            name=n.name,
            consumer_name=n.consumer_name,
            description=n.description,
            set_name=f"NOFORMATS-LF{lf_index}",
            origin_reference=n.origin,
        )


def create_from_dlisio(in_logical_files: list[dlisio.dlis.LogicalFile], minimal: str) -> DLISFile:
    """
    Write a DLIS file from a dlisio object.

    Args:
        in_logical_files: Logical files read with dlisio library
        minimal: if True, just the logical files, origins, frames and channels are passed to the output file

    Raises:
        ImportError: If dlisio is not installed.
    """

    out_logical_files = []

    first_logical_file = in_logical_files[0]

    in_SUL = first_logical_file.storage_label()

    out_physical_file_storage_label = StorageUnitLabel(
        in_SUL["id"], in_SUL["sequence"], in_SUL["maxlen"]
    )

    dlisFile = DLISFile(
        storage_unit_label=out_physical_file_storage_label,
    )

    for idx_lf, lf in enumerate(in_logical_files):

        # First, adding a logical file and its header to the DLIS file

        in_fheader = lf.fileheader

        in_fheaderid_truncated = in_fheader.id
        # max header id length (rp66v1 section 5.1.)
        if len(in_fheader.id) > eflr_types.FileHeaderItem.header_id_length_limit:
            in_fheaderid_truncated = in_fheader.id[:eflr_types.FileHeaderItem.header_id_length_limit]

        out_logical_file = dlisFile.add_logical_file(
            fh_id=in_fheaderid_truncated,
            fh_sequence_number=int(in_fheader.sequencenr),
            fh_identifier="0"  # single-character. This is specific to dliswriter
        )

        out_logical_files.append(out_logical_file)

        add_origins(lf, out_logical_files[idx_lf], idx_lf)

        if minimal.lower() == "false":
            add_axes(lf, out_logical_files[idx_lf], idx_lf)
            add_measurements(lf, out_logical_files[idx_lf], idx_lf)
            add_equipments(lf, out_logical_files[idx_lf], idx_lf)
            add_wellrefs(lf, out_logical_files[idx_lf], idx_lf)
            add_zones(lf, out_logical_files[idx_lf], idx_lf)
            add_longnames(lf, out_logical_files[idx_lf], idx_lf)
            add_calibration_coefficients(lf, out_logical_files[idx_lf], idx_lf)

        add_channels_and_frames(lf, out_logical_files[idx_lf], idx_lf)

        if minimal.lower() == "false":
            add_parameters(lf, out_logical_files[idx_lf], idx_lf)
            add_calibrations(lf, out_logical_files[idx_lf], idx_lf)
            add_comments(lf, out_logical_files[idx_lf], idx_lf)
            add_processes(lf, out_logical_files[idx_lf], idx_lf)
            add_computations(lf, out_logical_files[idx_lf], idx_lf)
            add_messages(lf, out_logical_files[idx_lf], idx_lf)
            add_groups(lf, out_logical_files[idx_lf], idx_lf)
            add_paths(lf, out_logical_files[idx_lf], idx_lf)
            add_splices(lf, out_logical_files[idx_lf], idx_lf)
            add_tools(lf, out_logical_files[idx_lf], idx_lf)
            add_noformats(lf, out_logical_files[idx_lf], idx_lf)

            # Channels, Computations and Measurements can have references to any objects. We set them here

            out_channels: list[eflr_types.ChannelItem] = \
                list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))

            for idx_c, out_c in enumerate(out_channels):
                ref_source = find_in_dliswriter(out_logical_file, lf.channels[idx_c].source)
                out_c.source.value = ref_source

            out_computations: list[eflr_types.ComputationItem] = \
                list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.ComputationSet))

            out_measurements: list[eflr_types.CalibrationMeasurementItem] = \
                list(out_logical_file._eflr_sets.get_all_items_for_set_type(eflr_types.CalibrationMeasurementSet))

            for idx_c, out_cp in enumerate(out_computations):
                ref_source = find_in_dliswriter(out_logical_file, lf.computations[idx_c].source)
                out_cp.source.value = ref_source

            for idx_m, out_m in enumerate(out_measurements):
                ref_source = find_in_dliswriter(out_logical_file, lf.measurements[idx_m].source)
                out_m.measurement_source.value = ref_source

    return dlisFile
