import re

from dlis_writer.configuration import global_config


HC_NAME_PATTERN = re.compile(r"[A-Z0-9_-]+")


def check_name_compatibility(name: str) -> None:
    if not isinstance(name, str):
        raise TypeError(f"Expected a str, got {type(name)}: {name}")

    if not global_config.high_compat_mode:
        return None

    if HC_NAME_PATTERN.fullmatch(name) is None:
        raise ValueError("In high-compatibility mode, object names can contain only uppercase characters, digits, "
                         f"dashes, and underscores; got {repr(name)}")


