from dlis_writer.file.file import DLISFile

from tests.dlis_files_for_testing.common import make_sul, make_file_header


def test_adding_origin_after_other_objects():
    df = DLISFile(storage_unit_label=make_sul(), file_header=make_file_header())

    ch_depth = df.add_channel(name="depth")
    ch_rpm = df.add_channel(name="surface rpm")

    origin = df.add_origin("DEFINING ORIGIN", file_set_number=38)

    ch_time = df.add_channel('time')
    frame = df.add_frame("MAIN FRAME", channels=(ch_time, ch_rpm, ch_depth))

    for obj in (ch_time, ch_rpm, ch_depth, frame, origin):
        assert obj.origin_reference == 38


def test_specifying_other_origin_reference():
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
