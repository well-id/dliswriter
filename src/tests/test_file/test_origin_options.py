from dlis_writer.file.file import DLISFile

from tests.dlis_files_for_testing.common import make_sul, make_file_header


def test_adding_origin_after_other_objects() -> None:
    df = DLISFile(storage_unit_label=make_sul(), file_header=make_file_header())

    ch_depth = df.add_channel(name="depth")
    ch_rpm = df.add_channel(name="surface rpm")

    assert df.default_origin_reference is None
    origin = df.add_origin("DEFINING ORIGIN", file_set_number=38)
    assert df.default_origin_reference == 38

    ch_time = df.add_channel('time')
    frame = df.add_frame("MAIN FRAME", channels=(ch_time, ch_rpm, ch_depth))

    for obj in (ch_time, ch_rpm, ch_depth, frame, origin):
        assert obj.origin_reference == 38


def test_specifying_other_origin_reference() -> None:
    df = DLISFile(storage_unit_label=make_sul(), file_header=make_file_header())

    ch_depth = df.add_channel(name="depth")
    ch_rpm = df.add_channel(name="surface rpm", origin_reference=22)

    origin = df.add_origin("DEFINING ORIGIN", file_set_number=38)

    ch_time = df.add_channel('time', origin_reference=15)
    ch_x = df.add_channel('x')
    frame = df.add_frame("MAIN FRAME", channels=(ch_time, ch_rpm, ch_depth, ch_x), origin_reference=10)

    for obj in (ch_depth, ch_x, origin):
        assert obj.origin_reference == 38

    assert frame.origin_reference == 10
    assert ch_time.origin_reference == 15
    assert ch_rpm.origin_reference == 22


def test_multiple_origins() -> None:
    df = DLISFile(storage_unit_label=make_sul(), file_header=make_file_header())

    assert df.default_origin_reference is None
    origin1 = df.add_origin("MAIN ORIGIN", file_set_number=23)
    assert df.default_origin_reference == 23
    axis1 = df.add_axis('AX1')
    ch1 = df.add_channel('rpm')

    origin2 = df.add_origin("ADDITIONAL ORIGIN", file_set_number=11)
    comp1 = df.add_computation("comp1", origin_reference=origin2.file_set_number.value)
    comp2 = df.add_computation("comp2")  # should have origin1 as reference
    assert df.default_origin_reference == 23

    origin3 = df.add_origin("ANOTHER ORIGIN")
    param1 = df.add_parameter("PARAM1", origin_reference=11)  # origin2
    param2 = df.add_parameter("PARAM2")  # origin1
    param3 = df.add_parameter("PARAM3", origin_reference=origin3.file_set_number.value)
    assert df.default_origin_reference == 23

    for obj in (origin1, axis1, ch1, comp2, param2):
        assert obj.origin_reference == 23

    for obj in (origin2, comp1, param1):
        assert obj.origin_reference == 11

    for obj in (origin3, param3):
        assert obj.origin_reference == origin3.file_set_number.value
