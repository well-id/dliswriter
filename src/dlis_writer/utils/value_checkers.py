import re

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
