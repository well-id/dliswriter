from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Frame(EFLR):
    set_type = 'FRAME'
    logical_record_type = LogicalRecordType.FRAME
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.description = self._create_attribute('description')
        self.channels = self._create_attribute('channels')
        self.index_type = self._create_attribute('index_type')
        self.direction = self._create_attribute('direction')
        self.spacing = self._create_attribute('spacing')
        self.encrypted = self._create_attribute('encrypted')
        self.index_min = self._create_attribute('index_min')
        self.index_max = self._create_attribute('index_max')
