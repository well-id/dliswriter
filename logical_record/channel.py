from typing import Union

from .utils.core import EFLR
from logical_record.utils.converters import get_representation_code
from logical_record.utils.enums import RepresentationCode, Units


class Channel(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'CHANNL'
        self.set_type = 'CHANNEL'

        self.long_name = None
        self.properties = None
        self.representation_code = None
        self.units = None
        self.dimension = None
        self.axis = None
        self.element_limit = None
        self.source = None
        self.minimum_value = None
        self.maximum_value = None

        self.create_attributes()
        self.data = None


def make_channel(name: str, dimension: int = 1, long_name: str = None, repr_code: RepresentationCode = None,
                 unit: Union[Units, str] = None, element_limit: int = None, data=None) -> Channel:
    """

    Args:
        name:
        dimension:
        long_name:
        repr_code:
        unit:
        element_limit:
        data:

    Returns:
        channel:
    """

    channel = Channel(name)
    channel.long_name.value = long_name or name
    channel.representation_code.value = get_representation_code(
        repr_code if repr_code is not None else RepresentationCode.FDOUBL)
    channel.dimension.value = [dimension]
    channel.element_limit.value = [element_limit if element_limit is not None else dimension]
    channel.data = data

    if unit is not None:
        channel.units.value = unit

    return channel

