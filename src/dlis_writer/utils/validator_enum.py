from enum import StrEnum
from typing import Union, Optional, Generator
import logging


logger = logging.getLogger(__name__)


class ValidatorEnum(StrEnum):

    @classmethod
    def get_values(cls) -> Generator:
        yield from cls.__members__.values()

    @classmethod
    def make_converter(cls, label: Optional[str] = None, make_uppercase: bool = False, allow_none: bool = False,
                       soft: bool = False):
        def converter(v: Union[str, None, "ValidatorEnum"]) -> Union[str, None]:
            if allow_none and v is None:
                return None

            if make_uppercase:
                v = v.upper().replace(' ', '-').replace('_', '-')

            if v in cls:
                if isinstance(v, cls):
                    return v.value
                return v

            if not isinstance(v, str):
                raise TypeError(f"Expected a str, got {type(v)}: {v}")

            try:
                v = cls[v]
            except KeyError:
                message = f"{repr(v)} is not one of the allowed {label or 'values'}: {', '.join(cls.get_values())}"
                if soft:
                    logger.warning(message)
                    return v
                else:
                    raise ValueError(message)
            return v.value

        return converter
