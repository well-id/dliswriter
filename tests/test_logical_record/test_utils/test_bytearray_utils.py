import pytest

from logical_record.utils.bytearray_utils import insert_and_shift


@pytest.mark.parametrize(('bt_arr', 'bt', 'pos'), (
        (bytearray(10), 17, 3),
        (bytearray(2), 1, 0),
        (bytearray(12), 3, 11),
        (bytearray([1, 3, 4, 0, 0, 0]), 2, 1),
        (bytearray([123, 12, 89, 32, 32, 56, 0]), 34, 4)
))
def test_insert_and_shift_single_byte(bt_arr, bt, pos):
    len_bt_arr = len(bt_arr)
    bt_arr_copy = bt_arr.copy()

    insert_and_shift(bt_arr, [bt], pos)

    assert len(bt_arr) == len_bt_arr
    assert bt_arr[pos] == bt

    assert bt_arr[:pos] == bt_arr_copy[:pos]
    assert bt_arr[pos+1:] == bt_arr_copy[pos:-1]


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos'), (
        (bytearray(3), b'\x12\x87\x03', 0),
        (bytearray(2), b'\x02', 1),
        (bytearray(12), b'\x01\x01\x02', 9),
        (bytearray([1, 5, 6, 0, 0, 0]), bytearray([2, 3, 4]), 1),
        (bytearray([123, 12, 89, 32, 32, 56, 0]), bytearray([0]), 4)
))
def test_insert_and_shift_multiple_bytes(bt_arr, bts, pos):
    len_bt_arr = len(bt_arr)
    len_bts = len(bts)
    bt_arr_copy = bt_arr.copy()

    insert_and_shift(bt_arr, bts, pos)

    assert len(bt_arr) == len_bt_arr
    assert bt_arr[pos:pos+len_bts] == bts

    assert bt_arr[:pos] == bt_arr_copy[:pos]
    assert bt_arr[pos+len_bts:] == bt_arr_copy[pos:-len_bts]


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos'), (
        (bytearray(2), b'\x12\x87\x03', 0),
        (bytearray(3), b'\x02', 3),
        (bytearray(12), b'\x01\x01\x02', 10),
        (bytearray([1, 5, 6, 0, 0, 0]), bytearray([2, 3, 4]), 5)
))
def test_cannot_insert_array_too_short(bt_arr, bts, pos):
    with pytest.raises(ValueError, match=f"Cannot insert bytes.* size {len(bt_arr)}"):
        insert_and_shift(bt_arr, bts, pos)


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos'), (
        (bytearray([1, 5, 6, 0, 0]), bytearray([2, 3, 4]), 2),
        (bytearray([0, 0, 0, 0, 0, 0, 0, 3]), b'\x02', 3),
        (bytearray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), b'\x01\x01\x02', 1),
        (bytearray([1, 2, 3, 0, 0, 5, 0]), b'\x12\x87\x03', 0),
))
def test_cannot_insert_tail_too_short(bt_arr, bts, pos):
    with pytest.raises(ValueError, match=f".*tail of the byte array is not long enough.*"):
        insert_and_shift(bt_arr, bts, pos)


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos', 'ref_bt_arr', 'end_data_pos'), (
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8]), 0, bytearray([8, 1, 2, 3, 0, 0]), 3),
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8]), 2, bytearray([1, 2, 8, 3, 0, 0]), 3),
        (bytearray([1, 2, 3, 4, 0, 0, 0]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 3, 4, 0]), 4),
))
def test_insert_with_data_end_specified(bt_arr, bts, pos, ref_bt_arr, end_data_pos):
    insert_and_shift(bt_arr, bts, pos, end_data_position=end_data_pos)
    assert bt_arr == ref_bt_arr


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos', 'ref_bt_arr', 'end_data_pos'), (
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8]), 0, bytearray([8, 2, 3, 0, 0, 0]), 0),
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8]), 2, bytearray([1, 2, 8, 0, 0, 0]), 2),
        (bytearray([1, 2, 3, 4, 5, 0, 0]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 5, 0, 0]), 1),
        (bytearray([1, 2, 3, 4, 0, 0, 0]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 3, 0, 0]), 3),
))
def test_insert_with_data_end_incorrectly_specified(bt_arr, bts, pos, ref_bt_arr, end_data_pos):
    insert_and_shift(bt_arr, bts, pos, end_data_position=end_data_pos)
    assert bt_arr == ref_bt_arr


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos', 'end_data_pos'), (
        (bytearray([1, 2, 3]), bytearray([8]), 0, 3),
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8]), 0, 6),
        (bytearray([1, 2, 3, 0, 0, 0]), bytearray([8, 9, 10]), 3, 4),
        (bytearray([1, 2, 3, 4, 5]), bytearray([8, 9]), 2, 5),
        (bytearray([1, 2, 3, 4, 0, 0, 0]), bytearray([8, 9]), 4, 6),
))
def test_insert_fail_with_data_end_too_large(bt_arr, bts, pos, end_data_pos):
    with pytest.raises(ValueError, match=" impossible without discarding relevant data"):
        insert_and_shift(bt_arr, bts, pos, end_data_position=end_data_pos)


@pytest.mark.parametrize(('bt_arr', 'bts', 'pos', 'ref_bt_arr', 'end_data_pos'), (
        (bytearray([1, 2, 3]), bytearray([8]), 0, bytearray([8, 1, 2]), 2),
        (bytearray([1, 2, 3]), bytearray([8]), 0, bytearray([8, 1, 3]), 1),
        (bytearray([1, 2, 3, 4, 5, 6]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 5, 6]), 2),
        (bytearray([1, 2, 3, 4, 5, 6]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 3, 6]), 3),
        (bytearray([1, 2, 3, 4, 5, 6]), bytearray([8, 9]), 2, bytearray([1, 2, 8, 9, 3, 4]), 4),
))
def test_array_tail_too_short_overriden_by_end_data_pos(bt_arr, bts, pos, ref_bt_arr, end_data_pos):
    insert_and_shift(bt_arr, bts, pos, end_data_position=end_data_pos)
    assert bt_arr == ref_bt_arr

