from sul import StorageUnitLabel



# STORAGE UNIT LABEL
storage_unit_sequence_number = 1
dlis_version = 'V1.00'
storage_unit_structure = 'RECORD'
max_record_length = 16384
storage_set_identifier = 'Default Storage Set'


# VISIBLE RECORD COMES NEXT BUT WE NEED TO CONSTRUCT THE LOGICAL FILE FIRST AND THEN CREATE THE VISIBLE RECORD



''' FOR EACH LOGICAL FILE '''

# LOGICAL FILE


''' FOR EACH LOGICAL RECORD SEGMENT IN A LOGICAL FILE '''

# LOGICAL RECORD SEGMENT

logical_record_segment_length = None

is_eflr = '1' # 1 or 0
has_predecessor_segment = '0' # 1 or 0
has_successor_segment = '0' # 1 or 0
is_encrypted = '0' # 1 or 0
has_encryption_protocol = '0' # 1 or 0
has_checksum = '0' # 1 or 0
has_trailing_length = '0' # 1 or 0
has_padding = '0' # 1 or 0





x = StorageUnitLabel()
print(x)