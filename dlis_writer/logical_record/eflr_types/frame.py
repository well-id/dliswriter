from configparser import ConfigParser
from typing_extensions import Self

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
        self.spacing = self._create_attribute('spacing', converter=float)
        self.encrypted = self._create_attribute('encrypted', converter=bool)
        self.index_min = self._create_attribute('index_min', converter=int)
        self.index_max = self._create_attribute('index_max', converter=int)

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        if not config.has_section("Frame.attributes"):
            pass
        if any(s in config["Frame.attributes"].keys() for s in ("channels", "channels.value")):
            raise RuntimeError("Frame channels cannot be defined from the 'Frame.attributes' config section")

        return super().from_config(config)


