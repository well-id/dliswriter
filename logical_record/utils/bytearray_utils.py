def insert_and_shift(byte_arr, bytes_to_insert, insert_position, end_data_position=None, check_tail=True):

    # how many bytes will be inserted
    n_bytes_to_insert = len(bytes_to_insert)

    # index of the end of the inserted part
    end_insert_position = insert_position + n_bytes_to_insert

    # total length of the byte array operated on
    total_n_bytes = len(byte_arr)

    if end_insert_position > total_n_bytes:
        raise ValueError(f"Cannot insert bytes at positions {insert_position}:{end_insert_position} "
                         f"into a byte array of size {total_n_bytes}")

    if end_data_position is None:
        # default - we don't know where relevant data end in the byte array
        # assume it's until the end minus the number of bytes we're going to insert
        end_data_position = total_n_bytes - n_bytes_to_insert  # discarded tail will be <n_bytes_to_insert> long
        new_end_data_position = None  # till the end of the byte array

        # if 'check_tail' - verify that the number of zeros at the end is at least as long as the n. bytes to insert
        if check_tail and byte_arr[-n_bytes_to_insert:].count(0) != n_bytes_to_insert:
            raise ValueError("The 0-filled tail of the byte array is not long enough "
                             f"to insert and shift  by {n_bytes_to_insert}")

    else:
        # the position at which relevant data should end has been provided by the user
        # assume it's correct, only check it against the total length of the original byte array
        # (both end_data_position and new_end_data position should be smaller than the length of the array,
        # but it's sufficient to only check the latter)
        new_end_data_position = end_data_position + n_bytes_to_insert
        if new_end_data_position > total_n_bytes:
            raise ValueError(f"Inserting {n_bytes_to_insert} into array of length {total_n_bytes}, filled with data "
                             f"until position {end_data_position} is impossible without discarding relevant data")

    # shift the bytes already at the insert position right by as many bytes as will be inserted; discards the tail
    byte_arr[end_insert_position:new_end_data_position] = byte_arr[insert_position:end_data_position]

    # insert the specified bytes in the desired position
    byte_arr[insert_position:end_insert_position] = bytes_to_insert
