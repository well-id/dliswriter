def insert_and_shift(byte_arr, bytes_to_insert, insert_position, check_tail=True):

    # how many bytes will be inserted
    n_bytes_to_insert = len(bytes_to_insert)

    # index of the end of the inserted part
    end_insert_position = insert_position + n_bytes_to_insert

    if end_insert_position > (nb := len(byte_arr)):
        raise ValueError(f"Cannot insert bytes at positions {insert_position}:{end_insert_position} "
                         f"into a byte array of size {nb}")

    if check_tail and byte_arr[-n_bytes_to_insert:].count(0) != n_bytes_to_insert:
        raise ValueError("The 0-filled tail of the byte array is not long enough "
                         f"to insert and shift  by {n_bytes_to_insert}")

    # shift the bytes already at the insert position right by as many bytes as will be inserted; discards the tail
    byte_arr[end_insert_position:] = byte_arr[insert_position:-n_bytes_to_insert]

    # insert the specified bytes in the desired position
    byte_arr[insert_position:end_insert_position] = bytes_to_insert
