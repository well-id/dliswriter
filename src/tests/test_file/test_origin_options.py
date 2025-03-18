from dliswriter.file.file import DLISFile

from tests.dlis_files_for_testing.common import make_sul, make_file_header


def test_adding_origin_after_other_objects() -> None:
    df = DLISFile(storage_unit_label=make_sul())
    lf = df.add_logical_file(file_header=make_file_header())

    ch_depth = lf.add_channel(name="depth")
    ch_rpm = lf.add_channel(name="surface rpm")

    assert lf.default_origin_reference is None
    origin = lf.add_origin("DEFINING ORIGIN", file_set_number=38)
    assert lf.default_origin_reference == 0

    ch_time = lf.add_channel("time")
    frame = lf.add_frame("MAIN FRAME", channels=(ch_time, ch_rpm, ch_depth))

    for obj in (ch_time, ch_rpm, ch_depth, frame, origin):
        assert obj.origin_reference == 0


def test_specifying_other_origin_reference() -> None:
    df = DLISFile(storage_unit_label=make_sul())
    lf = df.add_logical_file(file_header=make_file_header())

    ch_depth = lf.add_channel(name="depth")
    ch_rpm = lf.add_channel(name="surface rpm", origin_reference=22)

    origin = lf.add_origin("DEFINING ORIGIN", origin_reference=38)

    ch_time = lf.add_channel("time", origin_reference=15)
    ch_x = lf.add_channel("x")
    frame = lf.add_frame(
        "MAIN FRAME", channels=(ch_time, ch_rpm, ch_depth, ch_x), origin_reference=10
    )

    # Items created before the logical file's defining origin (i.e., the first origin) assume the defining origin's
    # origin_reference value when it is created. This value is also assigned to items created after the defining
    # origin with no origin_reference as creation argument
    for obj in (ch_depth, ch_x, origin):
        assert obj.origin_reference == 38

    assert frame.origin_reference == 10
    assert ch_time.origin_reference == 15
    assert ch_rpm.origin_reference == 22


def test_multiple_origins() -> None:
    df = DLISFile(storage_unit_label=make_sul())
    lf = df.add_logical_file(file_header=make_file_header())

    assert lf.default_origin_reference is None
    origin1 = lf.add_origin("MAIN ORIGIN", origin_reference=23)
    assert lf.default_origin_reference == 23
    axis1 = lf.add_axis("AX1")
    ch1 = lf.add_channel("rpm")

    origin2 = lf.add_origin("ADDITIONAL ORIGIN", origin_reference=11)
    comp1 = lf.add_computation("comp1", origin_reference=origin2.origin_reference)
    comp2 = lf.add_computation("comp2")  # should have origin1 as reference
    assert lf.default_origin_reference == 23

    param1 = lf.add_parameter("PARAM1", origin_reference=11)  # origin2
    param2 = lf.add_parameter("PARAM2")  # origin1
    assert lf.default_origin_reference == 23

    for obj in (origin1, axis1, ch1, comp2, param2):
        assert obj.origin_reference == 23

    for obj in (origin2, comp1, param1):
        assert obj.origin_reference == 11
