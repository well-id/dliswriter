import re
from typing import Union

from dlis_writer.configuration import global_config


HC_STRING_PATTERN = re.compile(r"[A-Z0-9_-]+")


def check_string_compatibility(s: str) -> None:
    if not isinstance(s, str):
        raise TypeError(f"Expected a str, got {type(s)}: {s}")

    if not global_config.high_compat_mode:
        return None

    if HC_STRING_PATTERN.fullmatch(s) is None:
        raise ValueError("In high-compatibility mode, strings can contain only uppercase characters, digits, "
                         f"dashes, and underscores; got {repr(s)}")


def validate_string(s: str) -> str:
    check_string_compatibility(s)
    return s


def convert_numeric(value: str) -> Union[int, float, str]:
    """Convert a string to an integer or float."""

    parser = float if '.' in value else int

    try:
        value = parser(value)
    except ValueError:
        raise ValueError(f"Value '{value}' could not be converted to a numeric type")
    return value


def convert_maybe_numeric(val: Union[str, int, float]) -> Union[str, int, float]:
    """Try converting a value to a number. If that fails, return the value unchanged."""

    if isinstance(val, (int, float)):
        return val

    if not isinstance(val, str):
        raise TypeError(f"Expected an int, float, or str; got {type(val)}: {val}")
    try:
        return convert_numeric(val)
    except ValueError:
        pass
    return val
