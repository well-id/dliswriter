import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class ProcessObject(EFLRObject):
    """Model an object being part of Process EFLR."""

    parent: "Process"

    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')  #: allowed values of the 'status' Attribute

    def __init__(self, name: str, **kwargs):
        """Initialise ProcessObject.

        Args:
            name        :   Name of the ProcessObject.
            **kwargs    :   Values of to be set as characteristics of the ProcessObject Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.version = Attribute('version', representation_code=RepC.ASCII, parent_eflr=self)
        self.properties = Attribute('properties', representation_code=RepC.IDENT, multivalued=True, parent_eflr=self)
        self.status = Attribute('status', converter=self.check_status, representation_code=RepC.IDENT, parent_eflr=self)
        self.input_channels = EFLRAttribute(
            'input_channels', object_class=Channel, multivalued=True, parent_eflr=self)
        self.output_channels = EFLRAttribute(
            'output_channels', object_class=Channel, multivalued=True, parent_eflr=self)
        self.input_computations = EFLRAttribute(
            'input_computations', object_class=Computation, multivalued=True, parent_eflr=self)
        self.output_computations = EFLRAttribute(
            'output_computations', object_class=Computation, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=Parameter, multivalued=True, parent_eflr=self)
        self.comments = Attribute('comments', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)

    @classmethod
    def check_status(cls, status):
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status


class Process(EFLR):
    """Model Process EFLR."""

    set_type = 'PROCESS'
    logical_record_type = EFLRType.STATIC
    object_type = ProcessObject


ProcessObject.parent_eflr_class = Process
