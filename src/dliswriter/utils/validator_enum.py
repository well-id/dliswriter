from enum import Enum
from typing import Union, Optional, Callable
import logging

from dliswriter.configuration import global_config


logger = logging.getLogger(__name__)


class ValidatorEnum(Enum):
    """Define an enum with a converter defining ability.

    The 'make_converter' method returns a callable which verifies whether a provided value can be found among the
    enum's members or their values. It then returns the value of the relevant member or raises an error if no fitting
    member is found.

    The enum's values are expected to be strings.
    """

    @classmethod
    def make_converter(cls, label: Optional[str] = None, allow_none: bool = False, soft: bool = False) -> Callable:
        def converter(v: Union[str, None, "ValidatorEnum"]) -> Union[str, None]:
            if allow_none and v is None:
                return None

            try:
                cls(v)
            except ValueError:
                pass
            else:
                if isinstance(v, cls):
                    return v.value
                return v

            if not isinstance(v, str):
                raise TypeError(f"Expected a str, got {type(v)}: {v}")

            message = (f"{repr(v)} is not one of the allowed {label or 'values'}: "
                       f"{', '.join(v.value for v in cls.__members__.values())}")
            if soft and not global_config.high_compat_mode:
                logger.warning(message)
                return v
            else:
                raise ValueError(message)

        return converter
