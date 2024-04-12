from contextlib import contextmanager
from typing import Generator, Callable, Any
import functools

from dliswriter.configuration import global_config


@contextmanager
def high_compatibility_mode() -> Generator:
    """Context manager. Turn on DLIS Writer's high-compatibility mode for the scope of the context."""

    arch = global_config.high_compat_mode
    global_config.high_compat_mode = True

    try:
        yield
    finally:
        global_config.high_compat_mode = arch


def high_compatibility_mode_decorator(func: Callable) -> Callable:

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        with high_compatibility_mode():
            func(*args, **kwargs)

    return wrapper
