import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType


logger = logging.getLogger(__name__)


class Process(EFLR):
    set_type = 'PROCESS'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.trademark_name = self._create_attribute('trademark_name')
        self.version = self._create_attribute('version')
        self.properties = self._create_attribute('properties')
        self.status = self._create_attribute('status')
        self.input_channels = self._create_attribute('input_channels')
        self.output_channels = self._create_attribute('output_channels')
        self.input_computations = self._create_attribute('input_computations')
        self.output_computations = self._create_attribute('output_computations')
        self.parameters = self._create_attribute('parameters')
        self.comments = self._create_attribute('comments')

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'input_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'output_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'input_computations', Computation)
        obj.add_dependent_objects_from_config(config, 'output_computations', Computation)
        obj.add_dependent_objects_from_config(config, 'parameters', Parameter)

        return obj
