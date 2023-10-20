import logging
from typing_extensions import Self
from configparser import ConfigParser
import importlib

from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import LogicalRecordType


logger = logging.getLogger(__name__)


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.object_type = self._create_attribute('object_type')
        self.object_list = self._create_attribute('object_list')
        self.group_list = self._create_attribute('group_list')

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        key = key or cls.__name__
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'group_list', Group)

        if 'object_list' in config[key]:
            obj.add_object_list(config, config[key]['object_list'])

        return obj

    def add_object_list(self, config, object_names):
        object_names = self.convert_values(object_names)
        if not object_names:
            return

        objects = []

        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        for object_name in object_names:
            class_name = object_name.split('-')[0]
            the_class = getattr(module, class_name, None)
            if the_class is None:
                raise ValueError(f"No EFLR class of name '{class_name}' found")

            objects.append(the_class.get_or_make_from_config(object_name, config))

        self.object_list.value = objects

