import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRListAttribute, ListAttribute


logger = logging.getLogger(__name__)


class Process(EFLR):
    set_type = 'PROCESS'
    logical_record_type = LogicalRecordType.STATIC
    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII)
        self.version = Attribute('version', representation_code=RepC.ASCII)
        self.properties = ListAttribute('properties', representation_code=RepC.IDENT)
        self.status = Attribute('status', converter=self.check_status, representation_code=RepC.IDENT)
        self.input_channels = EFLRListAttribute('input_channels', object_class=Channel)
        self.output_channels = EFLRListAttribute('output_channels', object_class=Channel)
        self.input_computations = EFLRListAttribute('input_computations', object_class=Computation)
        self.output_computations = EFLRListAttribute('output_computations', object_class=Computation)
        self.parameters = EFLRListAttribute('parameters', object_class=Parameter)
        self.comments = ListAttribute('comments', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)

    @classmethod
    def check_status(cls, status):
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.input_channels, obj.output_channels, obj.input_computations, obj.output_computations,
                     obj.parameters):
            attr.finalise_from_config(config)

        return obj
